'''
 Crud operations for database 
 This file includes create delete update and get 
 functions for creating database.
 Used in flask_api file.
 '''

import sys
import os

# Add backend 
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from database import create_connection
from models import Patient
from pydantic import ValidationError

connection, cursor = create_connection()

# Add appointment to database
def add_appointment(name: str, surname: str, personal_id: str, date: str, time: str, description: str):
    try:
        # Check the parameters with pydantic model
        patient = Patient(
            name=name,
            surname=surname,
            personal_id=personal_id,
            date=date,
            time=time,
            description=description
        )
    except ValidationError as e:
        print(f"Validation error: {e}")

    try:
        connection, cursor = create_connection()

        query = "INSERT INTO appointments (name, surname, personal_id, date, time, description) VALUES (?, ?, ?, ?, ?, ?)"
    
        cursor.execute(query, (patient.name, patient.surname, patient.personal_id, patient.date, patient.time, patient.description))
        connection.commit()
        connection.close()
        
    except Exception as e:
        print(f"Error adding appointment to database: {e}")

# Get patient informations by personal id
def get_patient_info(personal_id: str):
    try:
        connection, cursor = create_connection()

        query = "SELECT * FROM appointments WHERE personal_id = ?"
        cursor.execute(query, (personal_id,))
        patient = cursor.fetchall()
        connection.close()
        return patient

    except Exception as e:
        print(f"Error getting patient informations from database: {e}")

# Get all patient records from database
def get_all_appointments():
    try:
        connection, cursor = create_connection()

        query = "SELECT * FROM appointments"
        cursor.execute(query)
        appointments = cursor.fetchall()
        connection.close()
        return appointments
    except Exception as e:
        print(f"Error getting all patient records from database: {e}")

# Get appointment by id
def get_appointment_by_id(id: int):
    try:
        connection, cursor = create_connection()

        query = "SELECT * FROM appointments WHERE id = ?"
        cursor.execute(query, (id,))
        appointment = cursor.fetchall()
        connection.close()
        return appointment
    except Exception as e:
        print(f"Error getting appointment by id from database: {e}")

# Update appointment time or date by id
def update_appointment(id: int, date: str = None, time: str = None):
    connection, cursor = create_connection()
    
    try:
        # Check if date or time in correct format 
        if date and time:
            patient = Patient(date=date, time=time)
        # Date Check
        elif date:
            patient = Patient(date=date)  
        # Hour Check
        elif time:
            patient = Patient(time=time)  
        else:
            raise ValueError("Either date or time must be provided.")

        # Update the database
        if date and time:
            query = "UPDATE appointments SET date = ?, time = ? WHERE id = ?"
            cursor.execute(query, (patient.date, patient.time, id))
        elif date:
            query = "UPDATE appointments SET date = ? WHERE id = ?"
            cursor.execute(query, (patient.date, id))
        elif time:
            query = "UPDATE appointments SET time = ? WHERE id = ?"
            cursor.execute(query, (patient.time, id))

        # If id doesnt exist in the database
        if cursor.rowcount == 0:
            #raise HTTPException(status_code=404, detail="No appointment found with given id")
            return {"No appointment found with given id": str(e)}

        connection.commit()
    except ValidationError as e:
        print(f"Validation error: {e}")
        #raise HTTPException(status_code=400, detail=f"Validation error: {e}")
        return {"Validation error": str(e)}

    except Exception as e:
        print(f"Error updating appointment: {e}")
        #raise HTTPException(status_code=500, detail=f"Error updating appointment: {e}")
        return {"Error updating appointment": str(e)}

    finally:
        connection.close()


# Delete appointment by id
def delete_appointment(id: int):
    try:
        connection, cursor = create_connection()
        query = "DELETE FROM appointments WHERE id = ?"
        cursor.execute(query, (id,))
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"Error deleting appointment from database: {e}")

#Examples
#delete_appointment(7)
#add_appointment('Ahmet', 'Metin', '123454', '05-05-2025', '14:20', 'Stomachache')