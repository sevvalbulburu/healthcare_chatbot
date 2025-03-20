from fastapi import FastAPI, HTTPException
import uvicorn
from models import Patient
import crud

app = FastAPI()

# Add appointment 
@app.post("/appointments/")
def addAppointment(appointment: Patient):
     try:
          crud.add_appointment(appointment.name, 
                              appointment.surname, 
                              appointment.personal_id,
                              appointment.date,
                              appointment.time,
                              appointment.description)
          return {"message": "Appointment booked successfully"}
     except Exception as e:
          return {"message": str(e)}

# Get all appointments
@app.get("/appointments/")
def getAllAppointments():
     try:
          appointments = crud.get_all_appointments()
          if appointments:
               return {
                    "appointments": [
                         {"id": row[0], "name": row[1], "surname": row[2], "personal_id": row[3], 
                         "date": row[4], "time": row[5], "description": row[6]} 
                         for row in appointments
                    ]
               }                   
          else:
               return {"message": "No appointments found"}
     except Exception as e:
          return {"message": str(e)}

# Get appointment by id
@app.get("/appointments/{appointment_id}")
def getAppointment(appointment_id: int):
     try:
          app = crud.get_appointment_by_id(appointment_id)
          print(app)
          if not app:
               raise HTTPException(status_code=404, detail="Appointment not found")
          else:
               app = app[0]
               return {"id": app[0], "name": app[1], "surname": app[2], "personal_id": app[3],
                        "date": app[4], "time": app[5], "description": app[6]}
     except HTTPException as e:
          raise e
     except Exception as e:
          raise HTTPException(status_code=500, detail="Internal Server Error")

# Get patient info by personal id
@app.get("/appointments/{personal_id}")
def getPatientInfo(personal_id: str):
     try:
          patient = crud.get_patient_info(personal_id)
          if patient:
               general_info = {"name": patient[0][1], "surname": patient[0][2], "personal_id": patient[0][3]}
               appointment_info = [{"id": row[0], "date": row[4], "time": row[5], "description": row[6]}
                                   for row in patient]
               return{
                    "general_info": general_info,
                    "appointments": appointment_info
               }
          raise HTTPException(status_code=404, detail="Patient not found")
     except Exception as e:
          raise HTTPException(status_code=500, detail="Internal Server Error")

                  
# Update appointment date or time by id
@app.put("/appointments/{appointment_id}")
def updateAppointment(appointment_id: int, date : str = None, time : str = None):
     try:
          crud.update_appointment(appointment_id, date, time)
          return {"message": "Appointment updated successfully"}
     except Exception as e:
          raise HTTPException(status_code=400, detail="Invalid request")

# Delete appointment 
@app.delete("/appointments/{appointment_id}")
def deleteAppointment(appointment_id: int):
     try:
          crud.delete_appointment(appointment_id)
          return {"message": "Appointment deleted successfully"}
     except Exception as e:
          raise HTTPException(status_code=400, detail="Invalid request")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


