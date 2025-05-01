from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
import re

class UserSignupModel(BaseModel):
    name: str
    email: EmailStr
    password: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "john.doe@gmail.com",
                "password": "password123"
            }
        }, extra="forbid") # strict mode
    
    @field_validator('password')
    def validate_password(cls, password: str) -> str:
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            raise ValueError("Password must be alphanumeric")
        return password

class UserLoginModel(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "jane.doe@gmail.com",
                "password": "password123"
            }},
        extra="forbid") # strict mode