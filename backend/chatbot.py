import faiss
from openai import OpenAI
import numpy as np
from dotenv import load_dotenv
import os
import pandas as pd
from langchain.schema import Document
import requests
import json

load_dotenv()
faiss_path = "data_index.faiss"
chunks_path = "chunks.csv"

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("API_BASE_URL")
client = OpenAI(api_key=API_KEY)

# Load embeded indexes from faiss 
def load_faiss_index(faiss_path):
    index = faiss.read_index(faiss_path)
    return index

# Generate embedding for queries
def generate_embedding(query):
    response = client.embeddings.create(
        input = query,
        model="text-embedding-3-small"
    )
    # return as numpy array
    return np.array(response.data[0].embedding)

# Find smilar data indexes to query (Retrieval)
def retrieve_similar_data_indexes(query, faiss_index, k=5):
    # Generate embedding for query
    query_embedding = generate_embedding(query)

    # Search for similar data indexes
    distance, indexes = faiss_index.search(np.array([query_embedding]), k=k)
    return indexes[0]

# Analyze query's subject 
def analyze_request(query):
    prompt = f"""
    You are a medical assistant and appointment management system. Analyze the user's request and determine the following:
    1. What action is requested? (add_appointment, get_appointment_by_id, update_appointment, delete_appointment, get_patient_info, get_all_appointments or medical_question)
    2. Extract the necessary information from the request (name, surname, personal_id, date, time, description).
    3. If the date or time is given by the user, convert them to appropriate format (time: H:M date: DD-MM-YYYY).
    4. If the date is not spesific like "tomorrow, next week" do not add it to response.

    User's request: "{query}"

    Return the response in JSON format. For example:
    - If the user wants to create an appointment: {{"action": "add_appointment", "name": "Ahmet", "surname": "Yılmaz", "personal_id": "123456789", "date": "2023-10-15", "time": "14:00", "description": "Diyetisyen randevusu"}}
    - If the user wants to get an appointment: {{"action": "get_appointment_by_id", "appointment_id": 1}}
    - If the user asks a medical question: {{"action": "medical_question"}}
    - If the request is invalid: {{"action": "invalid"}}
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content), query

# Generate medical response response using RAG and OpenAI
def generate_med_response(query, similar_indexes, chunks):

    # Prepare the context from similar documents
    context = "\n".join([chunks[i].page_content for i in similar_indexes])

    # Prepare the prompt for OpenAI
    prompt = f"""
    You are a medical assistant. Answer the following question based on the provided context. 
    If the question is not relevant with the context, generate a polite response in the same 
    language as the question, expressing that you do not have information about this topic.

    Question: {query}

    Context:
    {context}
    """

    # Generate response using OpenAI
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful medical assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Get chunks from csv 
def get_chunks(csv_path):
    chunks_df = pd.read_csv("chunks.csv")
    chunks = [Document(page_content=row["chunk"]) for _, row in chunks_df.iterrows()]
    return chunks  

def handle_api_request(query, data):
    try:
        action = data["action"]
        res = ""
        if action == "add_appointment":
            required_fields = ["name", "surname", "personal_id", "date", "time"]
            for field in required_fields:
                if field not in data or not data[field]:
                    data[field] = input(f"Lütfen {field} bilgisini girin: ")
            res = requests.post(f"{BASE_URL}/appointments/", json=data)
            print("Randevu Oluşturma:", res.json())

        elif action == "get_appointment_by_id":
            if "appointment_id" not in data or not data["appointment_id"]:
                data["appointment_id"] = input("Lütfen randevu ID'sini girin: ")
            res = requests.get(f"{BASE_URL}/appointments/{data['appointment_id']}")
            print("Randevu Bilgisi:", res.json())

        elif action == "update_appointment":
            required_fields = ["appointment_id", "date", "time"]
            for field in required_fields:
                if field not in data or not data[field]:
                    data[field] = input(f"Lütfen {field} bilgisini girin: ")
            res = requests.put(f"{BASE_URL}/appointments/{data['appointment_id']}", json=data)
            print("Randevu Güncelleme:", res.json())

        elif action == "delete_appointment":
            if "appointment_id" not in data or not data["appointment_id"]:
                data["appointment_id"] = input("Lütfen randevu ID'sini girin: ")
            res = requests.delete(f"{BASE_URL}/appointments/{data['appointment_id']}")
            print("Randevu Silme:", res.json())

        elif action == "get_patient_info":
            if "personal_id" not in data or not data["personal_id"]:
                data["personal_id"] = input("Lütfen hasta ID'sini girin: ")
            res = requests.get(f"{BASE_URL}/appointments/{data['personal_id']}")
            print("Hasta Bilgisi:", res.json())

        elif action == "get_all_appointments":
            res = requests.get(f"{BASE_URL}/appointments/")
            print("Tüm Randevular:", res.json())
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Generate a response according to given {action} and response about the action {res} in same language with {query}"}
        ],
        )
        return response.choices[0].message.content

    except Exception as e:
        print("Hata:", e)

# Answer the medical question 
def handle_med_question(query, faiss_index, chunk_path):
    indexes = retrieve_similar_data_indexes(query=query, faiss_index=faiss_index)
    chunks = get_chunks(chunk_path)
    response = generate_med_response(query=query, similar_indexes=indexes, chunks=chunks)
    return response

def invalid_question(query):
    prompt = f"""
        Generate a polite response same language with the {query} that you don't know the subject.
        """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
    )
    return response.choices[0].message.content

def main_chatbot(query, faiss_index, chunk_path):
    answer = ""

    # Analayze the user's query
    response, original_query = analyze_request(query)
    action = response.get("action")

    # Medical query
    if action == "medical_question":
        answer = handle_med_question(query=original_query, faiss_index=faiss_index, chunk_path=chunk_path)

    # Invalid Request
    elif action == "invalid":
        answer = invalid_question()

    else:
        # API request for booking
        answer = handle_api_request(query=original_query, data=response)
    return answer



# EXAMPLE USAGE 
if __name__ == "__main__":

    index = load_faiss_index(faiss_path)


 



