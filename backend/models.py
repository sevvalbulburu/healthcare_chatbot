## Define models for database
from pydantic import BaseModel, field_validator
from datetime import datetime, date, time
from typing import Optional

class Patient(BaseModel):
     name: str = None
     surname: str = None 
     personal_id: str = None
     date: str = None # YYYY-MM-DD
     time: str = None # HH:MM 
     description: Optional[str] = None

     @field_validator("date")
     @classmethod
     def validate_date(cls, value):
          if value is None:
            return value
          try:
               datetime.strptime(value, "%d-%m-%Y")   
               return value
          except ValueError:
               raise ValueError("Date must be in DD-MM-YYYY format.")

     @field_validator("time")
     @classmethod
     def validate_time(cls, value):     
          if value is None:
               return value
          try:
               datetime.strptime(value, "%H:%M") 
               return value
          except ValueError:
               raise ValueError("Time must be in HH:MM format.")
