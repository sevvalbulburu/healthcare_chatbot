## This file is for creating api in pythonanywhere.

from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import ValidationError
import sys
import os
# Add the root path of the project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.crud import (
    add_appointment,
    get_appointment_by_id,
    get_patient_info,
    update_appointment,
    delete_appointment,
    get_all_appointments,
)
from backend.models import Patient

app = Flask(__name__)
CORS(app)  # CORS'u etkinleştir
@app.route("/")
def home():
    return "Welcome to the Healthcare Chatbot API!"

# Randevu oluşturma
@app.route("/appointments/", methods=["POST"])
def add_appointment_endpoint():
    try:
        data = request.json
        patient = Patient(
            name=data["name"],
            surname=data["surname"],
            personal_id=data["personal_id"],
            date=data["date"],
            time=data["time"],
            description=data["description"]
        )
        add_appointment(patient.name, patient.surname, patient.personal_id, patient.date, patient.time, patient.description)
        return jsonify({"message": "Appointment booked successfully"}), 201
    except ValidationError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# Tüm randevuları listeleme
@app.route("/appointments/", methods=["GET"])
def get_all_appointments_endpoint():
    try:
        appointments = get_all_appointments()
        if appointments:
            return jsonify({
                "appointments": [
                    {"id": row[0], "name": row[1], "surname": row[2], "personal_id": row[3], 
                     "date": row[4], "time": row[5], "description": row[6]} 
                    for row in appointments
                ]
            }), 200
        else:
            return jsonify({"message": "No appointments found"}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# Randevu sorgulama (ID ile)
@app.route("/appointments/<int:appointment_id>", methods=["GET"])
def get_appointment_endpoint(appointment_id):
    try:
        appointment = get_appointment_by_id(appointment_id)
        if not appointment:
            return jsonify({"message": "Appointment not found"}), 404
        else:
            appointment = appointment[0]
            return jsonify({
                "id": appointment[0],
                "name": appointment[1],
                "surname": appointment[2],
                "personal_id": appointment[3],
                "date": appointment[4],
                "time": appointment[5],
                "description": appointment[6]
            }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# Hasta bilgisi sorgulama (personal_id ile)
@app.route("/patients/<string:personal_id>", methods=["GET"])
def get_patient_info_endpoint(personal_id):
    try:
        patient = get_patient_info(personal_id)
        if not patient:
            return jsonify({"message": "Patient not found"}), 404
        else:
            general_info = {
                "name": patient[0][1],
                "surname": patient[0][2],
                "personal_id": patient[0][3]
            }
            appointment_info = [
                {"id": row[0], "date": row[4], "time": row[5], "description": row[6]}
                for row in patient
            ]
            return jsonify({
                "general_info": general_info,
                "appointments": appointment_info
            }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# Randevu güncelleme
@app.route("/appointments/<int:appointment_id>", methods=["PUT"])
def update_appointment_endpoint(appointment_id):
    try:
        data = request.json
        date = data.get("date")
        time = data.get("time")
        update_appointment(appointment_id, date, time)
        return jsonify({"message": "Appointment updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# Randevu silme
@app.route("/appointments/<int:appointment_id>", methods=["DELETE"])
def delete_appointment_endpoint(appointment_id):
    try:
        delete_appointment(appointment_id)
        return jsonify({"message": "Appointment deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# Uygulamayı çalıştır
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)