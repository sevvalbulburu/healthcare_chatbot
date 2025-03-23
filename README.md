## Healthcare Chatbot

This is a healthcare-focused chatbot designed to answer medical queries and manage appointments. It interacts with an API to handle booking operations and utilizes Retrieval-Augmented Generation (RAG) for processing medical data from Hugging Face. The chatbot UI is built with Gradio and can be accessed online via local hosting.

## Features
- **Appointment Management:** Interacts with a booking API to schedule, update, retrieve, and delete appointments.
- **Medical Query Processing:** Uses FAISS-based embedding search for handling medical-related questions.
- **Chatbot Agent:** Analyzes user queries, calls API endpoints, and handles invalid responses.
- **User Interface:** Built with Gradio for easy interaction, hosted with `share=True` for online accessibility.
- **SQLite Database:** Stores appointment data with full CRUD operations.

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sevvalbulburu/healthcare_chatbot.git
   ```
2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

## Project Structure
```
healthcare_chatbot/
│── backend/
│   │── flask_api.py        # Booking API created with Flask (Deployed on PythonAnywhere)
│   │── api_endpoints.py    # API endpoints used by the chatbot
│   │── chatbot.py          # Main chatbot logic (query analysis, RAG, API calls, etc.)
│   │── crud.py             # CRUD operations for managing appointments in the database
│   │── database.py         # SQLite database setup for appointment management
│   │── load_data.py        # Medical data processing and FAISS embedding
│   │── models.py           # Pydantic models for API and database schema
│
│── ui/
│   │── app.py              # Gradio-based UI for interacting with the chatbot
│
│── tests/
│   │── crud_test.py        # Unit tests for CRUD operations
│
│── requirements.txt        # Project dependencies
│── README.md               # Project documentation
```

## Running the Chatbot

1. **Access the API server:**
   The Flask API is deployed on PythonAnywhere. You can access it at:
   [svvlblbr.pythonanywhere.com](https://svvlblbr.pythonanywhere.com)

2. **Launch the Chatbot UI:**
   ```bash
   python ui/app.py
   ```
   The UI will be accessible via a shareable Gradio link.

## Dataset Files
Original medical dataset can be downloaded from:
[Huggingface Link](hf://datasets/codexist/medical_data/data/train-00000-of-00001.parquet)
Medical dataset files can be downloaded from:
[Google Drive Link](https://drive.google.com/drive/folders/1aQSwLBLIwGH5u9LwLCHGix9Qh6kbPp6v?usp=drive_link)

## Testing
Run unit tests for CRUD operations:
```bash
pytest tests/crud_test.py
```

## Notes
- Originally, the booking API was built with FastAPI, but it was later converted to Flask due to PythonAnywhere’s lack of FastAPI support.
- The Flask API is deployed as a web service on PythonAnywhere, requiring an account and proper setup to modify.
- The chatbot is designed for local hosting but can be accessed online with Gradio’s `share=True` feature.

## Contribution
Feel free to contribute by opening a pull request or reporting issues.

---

For further inquiries, contact [Şevval Bulburu](https://github.com/sevvalbulburu).
