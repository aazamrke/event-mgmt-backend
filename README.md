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

## API Documentation
Access interactive docs at `http://localhost:8000/docs`