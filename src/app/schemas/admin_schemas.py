from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class BlockUserRequest(BaseModel):
    to_block: bool


class ChangeRoleRequest(BaseModel):
    rol: str


class GetUserInfoResponse(BaseModel):
    id: str
    name: str
    last_name: str
    email: EmailStr
    role: str
    is_locked: bool
