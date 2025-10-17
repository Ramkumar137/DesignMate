#!/usr/bin/env python3
"""Setup database tables"""
from database import Base, engine

if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    print("You can now start the backend server.")
