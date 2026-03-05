from pydantic import BaseModel, EmailStr
from typing import Optional

#Registration form
class UserCreate(BaseModel):
    name: str
    last_name: str
    email: EmailStr #chek dot in to mail automaticly
    password: str
    role: str

#Form for logIn in system
class UserLogin(BaseModel):
    email: EmailStr
    password: str


#answer for for frontend
class UserResponse(BaseModel):
    name: str
    email: EmailStr
    
    class Config: 
        from_attributes = True #Tells Pydantic to read data from Python objects
    
    

    