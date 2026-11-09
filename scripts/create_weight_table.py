"""Script to create the weight_entries table"""
from app.core.database import engine, Base
from app.db.models import WeightEntry

if __name__ == "__main__":
    print("Creating weight_entries table...")
    Base.metadata.create_all(bind=engine)
    print("Table created successfully!")
