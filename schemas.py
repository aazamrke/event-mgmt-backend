from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
from models import UserRole, BookingStatus

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserPreferences(BaseModel):
    preferred_categories: List[int]

class CategoryResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class TimeSlotCreate(BaseModel):
    category_id: int
    start_time: datetime
    end_time: datetime
    max_capacity: int

class TimeSlotUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    max_capacity: Optional[int] = None

class TimeSlotResponse(BaseModel):
    id: int
    category_id: int
    start_time: datetime
    end_time: datetime
    max_capacity: int
    available_spots: int
    
    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    time_slot_id: int

class BookingResponse(BaseModel):
    id: int
    user_id: int
    time_slot_id: int
    status: BookingStatus
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str