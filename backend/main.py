from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn


app = FastAPI()

class QueryRequest(BaseModel):
     query: str

class AppointmentRequest(BaseModel):
     name: str
     date: str
     time: str


# Example
@app.get("/")
def read_root():
     return {"message": "Healthcare Chatbot API is running!"}

@app.post("/appointments")
def addAppointment():
     pass

@app.get("/appointments")
def getAppointment():
     pass

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
