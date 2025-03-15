import faiss
from openai import OpenAI
import numpy as np
from dotenv import load_dotenv
import os
import pandas as pd
from langchain.schema import Document


load_dotenv()
faiss_path = "data_index.faiss"
chunks_path = "chunks.csv"

API_KEY = os.getenv("OPENAI_API_KEY")
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

# Generate response using RAG and OpenAI
def generate_response(query, similar_indexes, chunks):

    # Prepare the context from similar documents
    context = "\n".join([chunks[i].page_content for i in similar_indexes])

    # Prepare the prompt for OpenAI
    prompt = f"""
    You are a medical assistant. Answer the following question based on the provided context.

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

# Generate the main chatbot 
def main_chatbot(query, faiss_index, chunk_path):
    indexes = retrieve_similar_data_indexes(query=query, faiss_index=faiss_index)
    chunks = get_chunks(chunk_path)
    response = generate_response(query=query, similar_indexes=indexes, chunks=chunks)
    return response


# EXAMPLE USAGE 
if __name__ == "__main__":

    index = load_faiss_index(faiss_path)

    ## Example query
    query = "What are the symptoms of Swyer-James syndrome?"
    response = main_chatbot(query=query, faiss_index=index, chunk_path=chunks_path)
    print("CHATBOT RESPONSE:\n",response)




