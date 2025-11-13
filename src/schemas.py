# src/schemas.py
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional

class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=100, description="User's password (min 8 chars)")

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()
    
    @validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: str
    role: str

class RecognizeRequest(BaseModel):
    receiver_id: int = Field(..., gt=0, description="ID of the user receiving recognition")
    credits: int = Field(..., gt=0, le=100, description="Number of credits to send (1-100)")
    note: Optional[str] = Field(None, max_length=500, description="Optional message")

    @validator('note')
    def note_must_be_valid(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v

class RedeemRequest(BaseModel):
    credits: int = Field(..., gt=0, le=10000, description="Number of credits to redeem")

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    grant_balance: int
    sent_this_month: int
    redeemable_balance: int
    total_received: int

    class Config:
        from_attributes = True

class RecognitionResponse(BaseModel):
    status: str
    recognition_id: int

class RedemptionResponse(BaseModel):
    status: str
    voucher_inr: int

class EndorsementResponse(BaseModel):
    status: str

class LeaderboardEntry(BaseModel):
    id: int
    name: str
    total_received: int
    recognition_count: int
    endorsement_total: int

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    entity_type: Optional[str]
    entity_id: Optional[int]
    details: Optional[dict]
    ip_address: Optional[str]
    ts: str  # ISO format datetime string
    
    class Config:
        from_attributes = True

