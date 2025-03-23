import gradio as gr
import os
import sys
# Import root path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.chatbot import load_faiss_index, analyze_request, handle_med_question, invalid_question, agent, check_missing_params
import json
from langdetect import detect 
import re
from datetime import datetime

# Faiss index ve chunk file paths for medical questions
faiss_path =  "C:/Users/sevva/Documents/GitHub/healthcare_chatbot/data_index.faiss" # Use your own path to file
chunks_path = "C:/Users/sevva/Documents/GitHub/healthcare_chatbot/chunks.csv" # Use your own path to file
index = load_faiss_index(faiss_path=faiss_path)

# Global Variables
missing_params = []
reset_status = True
data = {}

# Detect language 
def detect_language(text):
    try:
        lang = detect(text)
        return lang
    except:
        return "tr"  # Default Turkish

# Translate default message according to language
def get_translated_message(lang):
    translations = {
        "en": "Please provide the missing information:",
        "tr": "Eksik bilgileri girin:",
        "de": "Bitte geben Sie die fehlenden Informationen ein:",
        "fr": "Veuillez fournir les informations manquantes :",
        "es": "Por favor, proporcione la información faltante:",
    }
    return translations.get(lang, "Please provide the missing information:")  

def message_valid(missing_params, value):
    current_param = missing_params[0]

    if current_param == "name":
        return validate_name(value)
    elif current_param == "surname":
        return validate_surname(value)
    elif current_param == "personal_id":
        return validate_personal_id(value)
    elif current_param == "time":
        return validate_time(value)
    elif current_param == "date":
        return validate_date(value)
    elif current_param == "description":
        return validate_description(value)
    elif current_param == "appointment_id":
        return validate_appointment_id(value)
    else:
        print(f"Bilinmeyen parametre: {current_param}")
        return False
   
def validate_name(name):
    # Contains only letters and not be empty
    return bool(re.match(r"^[A-Za-z]+$", name)) and len(name) > 0

def validate_surname(surname):
    # Contains only letters and not be empty
    return bool(re.match(r"^[A-Za-z]+$", surname)) and len(surname) > 0

def validate_appointment_id(appointment_id):
    # Contains only digits and not be empty
    return bool(re.match(r"^[0-9]+$", appointment_id)) and len(appointment_id) > 0 

def validate_personal_id(personal_id):
    # Contain only digits and lenght is 6
    return bool(re.match(r"^\d{6}$", personal_id))

def validate_time(time):
    # Different time formats are accepted
    time_patterns = [
        r"^\d{2}:\d{2}$",  # HH:MM
        r"^\d{2}\.\d{2}$",  # HH.MM
        r"^\d{2}/\d{2}$",  # HH/MM
        r"^\d{4}$",  # HHMM
    ]
    for pattern in time_patterns:
        if re.match(pattern, time):
            return True
    return False

def validate_date(date):
    # English and Turkish month dictionary
    MONTHS = {
        "ocak": "january", "şubat": "february", "mart": "march", "nisan": "april",
        "mayıs": "may", "haziran": "june", "temmuz": "july", "ağustos": "august",
        "eylül": "september", "ekim": "october", "kasım": "november", "aralık": "december"
    }
    # Date regex patterns
    date_patterns = [
        (r"^\d{2}-\d{2}-\d{4}$", "%d-%m-%Y"),  # DD-MM-YYYY
        (r"^\d{2}\.\d{2}\.\d{4}$", "%d.%m.%Y"),  # DD.MM.YYYY
        (r"^\d{2}/\d{2}/\d{4}$", "%d/%m/%Y"),  # DD/MM/YYYY
        (r"^\d{4}-\d{2}-\d{2}$", "%Y-%m-%d"),  # YYYY-MM-DD
        (r"^\d{4}\.\d{2}\.\d{2}$", "%Y.%m.%d"),  # YYYY.MM.DD
        (r"^\d{4}/\d{2}/\d{2}$", "%Y/%m/%d"),  # YYYY/MM/DD
        (r"^\d{1,2}\s+([a-zA-Zğüşıöç]+)\s+\d{4}$", "%d %B %Y"),  # DD Month YYYY
    ]

    for pattern, date_format in date_patterns:
        match = re.match(pattern, date, re.IGNORECASE)
        if match:
            try:
                # If date is in format "15 haziran 2025" , convert month to english for check
                if "%d %B %Y" in date_format:
                    parts = date.split()
                    day = parts[0]
                    month = parts[1].lower()
                    year = parts[2]
                    
                    # If month is turkish, get english form 
                    month = MONTHS.get(month, month)

                    # Check the format 
                    date = f"{day} {month} {year}"

                # check if date valid datetime.strptime 
                datetime.strptime(date, date_format)
                return True
            except ValueError:
                return False  # Invalid (32 haziran 2025)

    return False 

def validate_description(description):
    # description lenght mest contain less than 500 letters and not be empty
    return len(description) > 0 and len(description) <= 500

# Function to handle responses
def respond(
    message,
    history: list[tuple[str, str]],
    system_message, 
    max_tokens,
    temperature,
    top_p,
):
    global missing_params, reset_status, data

    if reset_status:
        response = analyze_request(message)
        action = response.get("action")
        data = response  # data dictionary, includes JSON data from analyze_request
        data["query"] = message
        reset_status = False
    else:
        if message_valid(missing_params, message):
            data[missing_params[0]] = message
            missing_params.pop(0)
            if len(missing_params) == 0:
                # If missing parameters are None, Call API 
                input_data = json.dumps(data)  # Dictionary to JSON string
                result = agent.invoke({"input": input_data})
                missing_params, reset_status, data = [], True, {}
                return result["output"]  
            else:
                # If missing parameters exist
                lng = get_translated_message(detect_language(message))  
                response = f"{lng} {missing_params[0]}"
                return response        
        else:
            response = f"Wrong input. Please try again {missing_params[0]}:"
            return response

    # Medical Question
    if action == "medical_question":
        query = data["query"]
        missing_params, reset_status, data = [], True, {}
        return handle_med_question(query=query, faiss_index=index, chunk_path=chunks_path)
    # Invalid Question
    elif action == "invalid":
        missing_params, reset_status, data = [], True, {}
        return invalid_question(message)
    else:
        missing_params = check_missing_params(data)
        if len(missing_params) == 0:
            #  If missing parameters are None, Call API 
            input_data = json.dumps(data)  # Dictionary to JSON string
            result = agent.invoke({"input": input_data})
            missing_params, reset_status, data = [], True, {}
            return result["output"]  
        else:
            # If missing parameters exist
            lng = get_translated_message(detect_language(message))  
            response = f"{lng} {missing_params[0]}"
            return response


# Gradio ChatInterface
demo = gr.ChatInterface(
    respond,
    additional_inputs=[
        gr.Textbox(value="You are a friendly Chatbot.", label="System message"),
        gr.Slider(minimum=1, maximum=2048, value=512, step=1, label="Max new tokens"),
        gr.Slider(minimum=0.1, maximum=4.0, value=0.7, step=0.1, label="Temperature"),
        gr.Slider(
            minimum=0.1,
            maximum=1.0,
            value=0.95,
            step=0.05,
            label="Top-p (nucleus sampling)",
        ),
    ],
)

if __name__ == "__main__":
    demo.launch(share=True)
