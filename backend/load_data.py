from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd
import re
import numpy as np
import faiss
from openai import OpenAI
import concurrent.futures


API_KEY = "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"
df_link = "hf://datasets/codexist/medical_data/data/train-00000-of-00001.parquet"
client = OpenAI(api_key=API_KEY)

# Load the dataset from huggingface 
def load_data():
    # Login using e.g. `huggingface-cli login` to access this dataset
    df = pd.read_parquet(df_link)
    return df

#Preprocessing 
def clean_text(text):
    if not isinstance(text, str):  
        return ""  
    
    text = re.sub(r'\s+', ' ', text)  # Delete extra spaces 
    text = text.strip()  # Delete spaces from begining and end
    return text

#Chunk the dataset with langchain
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 150,
    length_function=len
)

# Generate embeddings using OpenAI
#def generate_embeddings(texts):
#    embeddings = []
#    for text in texts:
#        response = client.embeddings.create(
#            input=text,
#            model="text-embedding-3-small"
#        )
#        embedding = response.data[0].embedding
#        embeddings.append(embedding)
#    return np.array(embeddings)

def generate_embeddings(texts):
    def fetch_embedding(text, index):
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return index, response.data[0].embedding
    
    embeddings = [None] * len(texts)  # Result list 
    
    # Use parallel threading 
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_embedding, text, i): i for i, text in enumerate(texts)}
        
        for count, future in enumerate(concurrent.futures.as_completed(futures)):
            index, embedding = future.result()
            embeddings[index] = embedding  # Store the embedded texts as list 
            
            # Print progress 
            if (count + 1) % 500 == 0 or count + 1 == len(texts):
                print(f"Processed {count + 1}/{len(texts)} embeddings ({(count + 1) / len(texts) * 100:.2f}%)")
    
    return np.array(embeddings)

# Load the dataset and clean
df = load_data()
df["clean_data"] = df["data"].apply(clean_text)

# Create chunks
chunks = text_splitter.create_documents([df.to_string()])

# Return the chunks to dataframe and save as CSV file (Use the csv if needed to load the chunks)
#chunks_df = pd.DataFrame([chunk.page_content for chunk in chunks], columns=["chunk"])
#chunks_df.to_csv("chunks.csv", index=False)

# Generate embeddings for chunks
texts = [chunk.page_content for chunk in chunks]
print("Embeddings started to create")
embeddings = generate_embeddings(texts)
print("Embeddings created succesfully.")
# Save embeddings to a .npy file if needed
np.save("data_embeddings.npy", embeddings)

# Load embeddings from the .npy file (if needed)
# embeddings = np.load("medical_data_embeddings.npy")

# Save embeddings to FAISS
dimension = embeddings.shape[1]  
index = faiss.IndexFlatL2(dimension)  # L2 distance for similarity search
index.add(embeddings)

# Save the FAISS index to disk
faiss.write_index(index, "data_index.faiss")

print("Embeddings generated and saved to FAISS index and .npy file.")



