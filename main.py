from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import json

from database import get_db, create_tables
from models import User, EventCategory, TimeSlot, Booking, UserRole, BookingStatus
from schemas import *
from auth import verify_password, get_password_hash, create_access_token, verify_token

app = FastAPI(title="Event Management API")
security = HTTPBearer()

@app.on_event("startup")
def startup_event():
    create_tables()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user

@app.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    # Set admin role for admin@admin.com
    role = UserRole.ADMIN if user.email == "admin@admin.com" else UserRole.USER
    db_user = User(email=user.email, hashed_password=hashed_password, role=role)
    db.add(db_user)
    db.commit()
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(EventCategory).all()

@app.post("/user/preferences")
def set_preferences(preferences: UserPreferences, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.preferred_categories = json.dumps(preferences.preferred_categories)
    db.commit()
    return {"message": "Preferences updated"}

@app.get("/slots", response_model=List[TimeSlotResponse])
def get_slots(categories: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(TimeSlot)
    
    if categories:
        category_ids = [int(x) for x in categories.split(",")]
        query = query.filter(TimeSlot.category_id.in_(category_ids))
    
    slots = query.all()
    result = []
    
    for slot in slots:
        booked_count = db.query(Booking).filter(
            Booking.time_slot_id == slot.id,
            Booking.status == BookingStatus.BOOKED
        ).count()
        
        result.append(TimeSlotResponse(
            id=slot.id,
            category_id=slot.category_id,
            start_time=slot.start_time,
            end_time=slot.end_time,
            max_capacity=slot.max_capacity,
            available_spots=slot.max_capacity - booked_count
        ))
    
    return result

@app.post("/bookings", response_model=BookingResponse)
def create_booking(booking: BookingCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if slot exists
    slot = db.query(TimeSlot).filter(TimeSlot.id == booking.time_slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Time slot not found")
    
    # Check for double booking
    existing_booking = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.time_slot_id == booking.time_slot_id,
        Booking.status == BookingStatus.BOOKED
    ).first()
    
    if existing_booking:
        raise HTTPException(status_code=400, detail="Already booked this slot")
    
    # Check capacity
    booked_count = db.query(Booking).filter(
        Booking.time_slot_id == booking.time_slot_id,
        Booking.status == BookingStatus.BOOKED
    ).count()
    
    if booked_count >= slot.max_capacity:
        raise HTTPException(status_code=400, detail="Slot is full")
    
    db_booking = Booking(user_id=current_user.id, time_slot_id=booking.time_slot_id)
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    return db_booking

@app.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only cancel your own bookings")
    
    booking.status = BookingStatus.CANCELLED
    db.commit()
    return {"message": "Booking cancelled"}

@app.post("/admin/slots", response_model=TimeSlotResponse)
def create_slot(slot: TimeSlotCreate, admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    # Validate category exists
    category = db.query(EventCategory).filter(EventCategory.id == slot.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")
    
    db_slot = TimeSlot(**slot.dict())
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    
    return TimeSlotResponse(
        id=db_slot.id,
        category_id=db_slot.category_id,
        start_time=db_slot.start_time,
        end_time=db_slot.end_time,
        max_capacity=db_slot.max_capacity,
        available_spots=db_slot.max_capacity
    )

@app.put("/admin/slots/{slot_id}", response_model=TimeSlotResponse)
def update_slot(slot_id: int, slot_update: TimeSlotUpdate, admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    db_slot = db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()
    if not db_slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    for field, value in slot_update.dict(exclude_unset=True).items():
        setattr(db_slot, field, value)
    
    db.commit()
    
    booked_count = db.query(Booking).filter(
        Booking.time_slot_id == slot_id,
        Booking.status == BookingStatus.BOOKED
    ).count()
    
    return TimeSlotResponse(
        id=db_slot.id,
        category_id=db_slot.category_id,
        start_time=db_slot.start_time,
        end_time=db_slot.end_time,
        max_capacity=db_slot.max_capacity,
        available_spots=db_slot.max_capacity - booked_count
    )

@app.delete("/admin/slots/{slot_id}")
def delete_slot(slot_id: int, admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    db_slot = db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()
    if not db_slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    db.delete(db_slot)
    db.commit()
    return {"message": "Slot deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)