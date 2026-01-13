from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

Base = declarative_base()

class UserRole(PyEnum):
    USER = "USER"
    ADMIN = "ADMIN"

class BookingStatus(PyEnum):
    BOOKED = "BOOKED"
    CANCELLED = "CANCELLED"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    preferred_categories = Column(Text)  # JSON string of category IDs
    
    bookings = relationship("Booking", back_populates="user")

class EventCategory(Base):
    __tablename__ = "event_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
    time_slots = relationship("TimeSlot", back_populates="category")

class TimeSlot(Base):
    __tablename__ = "time_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("event_categories.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    max_capacity = Column(Integer)
    
    category = relationship("EventCategory", back_populates="time_slots")
    bookings = relationship("Booking", back_populates="time_slot")

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"))
    status = Column(Enum(BookingStatus), default=BookingStatus.BOOKED)
    
    user = relationship("User", back_populates="bookings")
    time_slot = relationship("TimeSlot", back_populates="bookings")