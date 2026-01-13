# Event Management Backend

A Python-based event booking platform allowing users to reserve predefined time slots via an interactive calendar interface. The backend is implemented in Python using FastAPI to handle business logic and persistence.

## Features
- JWT-based authentication
- Role-based access (USER/ADMIN)
- Event categories and time slot management
- Booking system with capacity control
- Business rules enforcement (no double booking)

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure PostgreSQL in `.env` file
3. Initialize database: `python init_db.py`
4. Run server: `python main.py`

## Admin Setup
To create admin users, manually update the user role in the database:
```sql
UPDATE users SET role = 'ADMIN' WHERE email = 'your-admin@email.com';
```

## API Endpoints

### Authentication
**POST /register**
- Input: `{"email": "user@example.com", "password": "password"}`
- Response: `{"access_token": "jwt_token", "token_type": "bearer"}`

**POST /login**
- Input: `{"email": "user@example.com", "password": "password"}`
- Response: `{"access_token": "jwt_token", "token_type": "bearer"}`

### Categories
**GET /categories**
- Input: None
- Response: `[{"id": 1, "name": "Cat 1"}]`

### User Preferences
**POST /user/preferences** (Requires Auth)
- Input: `{"preferred_categories": [1, 2]}`
- Response: `{"message": "Preferences updated"}`

### Time Slots
**GET /slots?categories=1,2**
- Input: Query param `categories` (optional)
- Response: `[{"id": 1, "category_id": 1, "start_time": "2024-01-01T10:00:00", "end_time": "2024-01-01T11:00:00", "max_capacity": 10, "available_spots": 8}]`

### Bookings
**POST /bookings** (Requires Auth)
- Input: `{"time_slot_id": 1}`
- Response: `{"id": 1, "user_id": 1, "time_slot_id": 1, "status": "BOOKED"}`

**DELETE /bookings/{booking_id}** (Requires Auth)
- Input: Path param `booking_id`
- Response: `{"message": "Booking cancelled"}`

### Admin Endpoints (Requires Admin Role)
**POST /admin/slots**
- Input: `{"category_id": 1, "start_time": "2024-01-01T10:00:00", "end_time": "2024-01-01T11:00:00", "max_capacity": 10}`
- Response: `{"id": 1, "category_id": 1, "start_time": "2024-01-01T10:00:00", "end_time": "2024-01-01T11:00:00", "max_capacity": 10, "available_spots": 10}`

**PUT /admin/slots/{slot_id}**
- Input: `{"max_capacity": 15}` (partial update)
- Response: `{"id": 1, "category_id": 1, "start_time": "2024-01-01T10:00:00", "end_time": "2024-01-01T11:00:00", "max_capacity": 15, "available_spots": 13}`

**DELETE /admin/slots/{slot_id}**
- Input: Path param `slot_id`
- Response: `{"message": "Slot deleted"}`

## API Documentation
Access interactive docs at `http://localhost:8000/docs`