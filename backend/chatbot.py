import faiss
from openai import OpenAI
import numpy as np
from dotenv import load_dotenv
import os
import sys
import pandas as pd
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.api_endpoints import add_appointment, get_all_appointments, get_appointment_by_id, update_appointment, delete_appointment
from langchain.agents import Tool
from langchain.prompts import PromptTemplate
import ast
from langchain.memory.buffer import ConversationBufferMemory

agent_prompt = PromptTemplate(
    input_variables=["input"],
    template="""
        You are an AI assistant that helps users schedule, update, and manage appointments via API calls.  
        When a user makes a request, check if all necessary parameters are provided.  
        - If any required parameter is missing, ask the user for the missing information before making the API call. 
        - If any required parameter is missing, DO NOT try to create missing parameters randomly. Return the missing parameters and ask them to user. 
        - Once all required data is collected, call the appropriate API endpoint and return the result in a user-friendly format.  
        - Maintain the same language as the user query when responding.  
        - Randevuları aşağıdaki formatla listele:
            Tarih: {date}, Saat: {time}, Ad Soyad: {name} {surname}, Açıklama: {description}

        Example flow:  
        User: "Schedule an appointment for John Doe on March 25 at 14:00"  
        → Assistant: "Please provide the personal ID and a short description for the appointment."  
        (User provides missing info)  
        → Assistant makes the API call and returns confirmation.  

        Follow this structure for all API interactions.
        You have to provide the answer maximum after 3 Thoughts. 



    Output will be below format:
    Thought: ...
    Action: ...
    Action Input: ...


    User Query: {input}
    """
)

load_dotenv()

faiss_path = "C:/Users/sevva/Documents/GitHub/healthcare_chatbot/data_index.faiss" # Use your own path to file
chunks_path = "C:/Users/sevva/Documents/GitHub/healthcare_chatbot/chunks.csv" # Use your own path to file

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
    1. What action is requested? (add_appointment, get_appointment_by_id, update_appointment, delete_appointment, get_all_appointments or medical_question)
    2. Extract the necessary information from the request (name, surname, personal_id, date, time, description).
    3. If the date or time is given by the user, convert them to appropriate format (time: H:M date: DD-MM-YYYY).
    4. If the date is not spesific like "tomorrow, next week" do not add it to response.
    5. Personal ID is an ID with 6 digit characters("123456"). Do not mix it with appointment ID.
    6. Personal ID can be write with only digits, Appointment ID can be write with digits or text.
    7. If appointment ID written in text, convert it to integer format. (EX: one -> 1)

    User's request: "{query}"

    Return the response in JSON format. For example:
    - If the user wants to create an appointment: {{"action": "add_appointment", "name": "Ahmet", "surname": "Yılmaz", "personal_id": "123456", "date": "2023-10-15", "time": "14:00", "description": "Diyetisyen randevusu"}}
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
    return ast.literal_eval(response.choices[0].message.content)

# Generate medical response response using RAG and OpenAI
def generate_med_response(query, similar_indexes, chunks):

    # Prepare the context from similar documents
    context = "\n".join([chunks[i].page_content for i in similar_indexes])
    print("CONTEXT: \n",context)

    # Prepare the prompt for OpenAI
    prompt = f"""
    You are a medical assistant. Answer the following question based on the provided context. 
    If the question is not relevant with the context, generate a polite response in the same 
    language as the question, expressing that you do not have information about this topic.
    If context inluced keywords in query, examine context and genarate closest answer.

    Question: {query}

    Context:
    {context}
    """

    # Generate response using OpenAI
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are a helpful medical assistant.Answer the questions based on {prompt}"},
            {"role": "user", "content": query}
        ]
    )
    return response.choices[0].message.content

# Get chunks from csv 
def get_chunks(csv_path):
    chunks_df = pd.read_csv(csv_path)
    chunks = [Document(page_content=row["chunk"]) for _, row in chunks_df.iterrows()]
    return chunks  

# Answer the medical question 
def handle_med_question(query, faiss_index, chunk_path):
    indexes = retrieve_similar_data_indexes(query=query, faiss_index=faiss_index)
    chunks = get_chunks(chunk_path)
    response = generate_med_response(query=query, similar_indexes=indexes, chunks=chunks)
    return response

# Create an Agent for API requests
def create_agent():
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", api_key=API_KEY)
    # Define the tools
    tools = [
        Tool(
            name="add_appointment",
            func=lambda data: add_appointment(data),
            description="Create an appointment. Parameters: name, surname, personal_id, date, time, description, query."
        ),
        Tool(
            name="update_appointment",
            func=lambda data: update_appointment(data),
            description="Update an appointment. Parameters: appointment_id, date, time, query."
        ),
        Tool(
            name="delete_appointment",
            func=lambda data: delete_appointment(data),
            description="Delete an appointment. Parameters: appointment_id, query."
        ),
        Tool(
            name="get_all_appointments",
            func=lambda data: get_all_appointments(),
            description="Get all appointments."
        ),
        Tool(
            name="get_appointment_by_id",
            func=lambda data: get_appointment_by_id(data),
            description="Get appointment details by ID. Parameters: appointment_id, query."
        )
    ]

    memory_assignment = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Agent'ı başlatın
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent_type=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        prompt=agent_prompt,
        handle_parsing_errors=True,
        memory=memory_assignment,
        max_iterations=5,
    )

    return agent

# Generate answer for invalid questions
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

# Checks missing parameters for API calls
def check_missing_params(data):
    action = data.get("action")
    if action == "get_all_appointments":
        return []

    elif action == "add_appointment":
        required_fields = ["name", "surname", "personal_id", "date", "time", "description"]
        missing_fields = [field for field in required_fields if not data.get(field)]
    
    elif action == "get_appointment_by_id":
        required_fields = ["appointment_id", "query"]
        missing_fields = [field for field in required_fields if not data.get(field)]
    
    elif action == "delete_appointment":
        required_fields = ["appointment_id", "query"]
        missing_fields = [field for field in required_fields if not data.get(field)]
    
    elif action == "update_appointment":
        required_fields = ["appointment_id", "date", "time"]
        missing_fields = [field for field in required_fields if not data.get(field)]
        print(missing_fields)
        if data.get("date") and not data.get("time"): missing_fields.remove("time")
        if data.get("time") and not data.get("date"): missing_fields.remove("date")
        
    return missing_fields

   
# Main chatbot app algırithm --> Same logic applied for UI in app.py
# def main_chatbot(query, faiss_index, chunk_path, missing_par_flag=0, context=None):
#     try:
#     
#         if missing_par_flag == 0:
#             response = analyze_request(query)
#             action = response.get("action")
#             data = response  # data dictionary'si, analyze_request'ten gelen JSON verisini içerir
#             data["query"] = query
#             context = data  # Bağlamı güncelle
#         else:
#             # Eksik bilgileri alırken, önceki bağlamı kullan
#             action = context.get("action")
#             data = context
#             data["query"] = query
#             context = None
    
#         # Tıbbi sorgu
#         if action == "medical_question":

#             return handle_med_question(query=query, faiss_index=faiss_index, chunk_path=chunk_path), context, 0

#         # Geçersiz istek
#         elif action == "invalid":
#             return invalid_question(query), context, 0

#         else:
#             # Eksik parametreleri kontrol et
#             missing_params = check_missing_params(data)
#             if missing_params:
#                 if isinstance(missing_params, list):
#                     missing_params = ", ".join(missing_params)
#                 return missing_params, data, 1  # missing_par_flag = 1

#             # Eksik parametre yoksa, API çağrısını yap
#             input_data = json.dumps(data)  # Dictionary'yi JSON string'e dönüştür
#             result = agent.invoke({"input": input_data})
#             return result["output"], context, 0  # missing_par_flag = 0

#     except Exception as e:
#         raise Exception(e)
    
index = load_faiss_index(faiss_path)
agent = create_agent()



