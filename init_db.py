from database import SessionLocal, create_tables
from models import EventCategory

def init_db():
    create_tables()
    db = SessionLocal()
    
    # Create default categories if they don't exist
    categories = ["Cat 1", "Cat 2", "Cat 3"]
    for cat_name in categories:
        if not db.query(EventCategory).filter(EventCategory.name == cat_name).first():
            category = EventCategory(name=cat_name)
            db.add(category)
    
    db.commit()
    db.close()
    print("Database initialized with default categories")

if __name__ == "__main__":
    init_db()