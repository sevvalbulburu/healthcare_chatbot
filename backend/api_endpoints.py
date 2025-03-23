# API endpoints for accesing the API from Interface 
import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("API_BASE_URL")


# Create Appointment Endpoint
def add_appointment(data):
    """
    Creates a new appointment with the given details.

    Args:
        data (dict): Dictionary containing appointment details.

    Returns:
        dict or AgentAction: API response or AgentAction to ask for missing fields.
    """
    try:
        if isinstance(data, str):
            data = json.loads(data)

        required_fields = ["name", "surname", "personal_id", "date", "time", "description"]

        # Check if data includes required fields
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            # Eksik parametreler varsa, kullanıcıya sor
            missing_fields_str = ", ".join(missing_fields)
            main_prompt = f"Generate a response with the same language in {data.get('query', 'tr')}. "

            return "The following fields are missing: {missing_fields_str}. Please provide the missing information."
        
        
        # Eğer eksik parametre yoksa, API çağrısını yap
        response = requests.post(f"{BASE_URL}/appointments", json=data)
        return response.json()

    except Exception as e:
        return {"error": str(e)}


# Update Appointment Endpoint
def update_appointment(data):
    """
    Updates an existing appointment with new date and/or time.

    Args:
        appointment_id (str): Unique identifier for the appointment.
        date (str, optional): New appointment date in YYYY-MM-DD format.
        time (str, optional): New appointment time in HH:MM format.
        query (str, optional): Language preference or additional query context.

    Returns:
        dict: API response or error message if required parameters are missing.
    """
    try:
        if isinstance(data, str):
            data = json.loads(data)
        # Dictionary'den appointment_id ve query'yi al
        appointment_id = data.get("appointment_id", str("mixed with personal id"))
        if appointment_id == "mixed with personal id":
            appointment_id = data.get("personal_id", "Not found") 
        if appointment_id == "Not found" or type(appointment_id) != int:
            raise Exception ("APPONTMENT ID NOT RECIEVED")

        date = data.get("date", None)
        time = data.get("time", None)

        # Check the appointment ID
        if not appointment_id:
            return {"error": "Appointment ID is required.'"}

        data = {"appointment_id": appointment_id}
        
        # Check for the optional parameters 
        if not date and not time:    
            return {"error": "At least one of the date or time is required."}
        
        if date:
            data["date"] = date
        if time:
            data["time"] = time

        # API Call
        response = requests.put(f"{BASE_URL}/appointments/{appointment_id}", json=data)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Get Appointment Information by Appointment ID
def get_appointment_by_id(data):
    """
    Retrieves an appointment's details using its unique appointment ID.

    Args:
        appointment_id (str): Unique identifier for the appointment.
        query (str, optional): Language preference or additional query context.

    Returns:
        dict: API response containing appointment details or error message.
    """
    try:
        if isinstance(data, str):
            data = json.loads(data)
        # Dictionary'den appointment_id ve query'yi al
        appointment_id = data.get("appointment_id")

    # Check the appointment ID
        if not appointment_id:
            return {"error" : "Appointment ID is required"}
        
        # API Call
        response = requests.get(f"{BASE_URL}/appointments/appointment_id/{appointment_id}")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Get Patient Info by Personal ID - Not Used
def get_patient_info(data):
    """
    Retrieves patient information using their personal ID.

    Args:
        personal_id (str): Unique identifier for the patient.
        query (str, optional): Language preference or additional query context.

    Returns:
        dict: API response containing patient information or error message.
    """
    try:
        # Check the personal ID
        if not data["personal_id"]:
            return {"error" : "Personal ID is required."}
        
        # API Call
        response = requests.get(f"{BASE_URL}/appointments/personal_id/{data["personal_id"]}")
        return response
    except Exception as e:
        return {"error": str(e)}

# Get All Booking Information
def get_all_appointments():
    """
    Retrieves a list of all appointments.

    Returns:
        dict: API response containing all appointment records.
    """
    try:
        # API Call
        response = requests.get(f"{BASE_URL}/appointments")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Delete an Appointment by Appointment ID
def delete_appointment(data):
    """
    Deletes an appointment using its unique appointment ID.

    Args:
        appointment_id (str): Unique identifier for the appointment.
        query (str, optional): Language preference or additional query context.

    Returns:
        dict: API response confirming deletion or error message.
    """
    try:
        if isinstance(data, str):
            data = json.loads(data)
        # Check the appointment ID
        if not data["appointment_id"]:
            return {"error": "Appointment ID must required"}
        # API Call
        response = requests.delete(f"{BASE_URL}/appointments/{data["appointment_id"]}")
        return response
    except Exception as e:
        return {"error": str(e)}
