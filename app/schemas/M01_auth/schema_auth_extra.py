from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterRequest(BaseModel):
    pessoa_id: Optional[str] = Field(None, description="UUID da pessoa já cadastrada")
    full_name: Optional[str] = Field(
        None, description="Nome completo (usado se pessoa_id não fornecido)"
    )
    username: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=6)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(...)


class ResetPasswordRequest(BaseModel):
    token: str = Field(...)
    new_password: str = Field(..., min_length=6)


class GenericMessage(BaseModel):
    message: str
