#!/usr/bin/env python3
"""
Startup script to ensure database tables exist
"""
import os
from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

def create_auth_tables():
    """Create authentication tables if they don't exist"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # Create users table
    users_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INT PRIMARY KEY AUTO_INCREMENT,
        email VARCHAR(255) UNIQUE NOT NULL,
        hashed_password VARCHAR(255) NOT NULL,
        full_name VARCHAR(255) NOT NULL,
        role VARCHAR(20) NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Create project_submissions table
    submissions_sql = """
    CREATE TABLE IF NOT EXISTS project_submissions (
        id INT PRIMARY KEY AUTO_INCREMENT,
        project_name VARCHAR(255) NOT NULL,
        idea TEXT NOT NULL,
        team_members VARCHAR(255),
        roll_number VARCHAR(50),
        class_name VARCHAR(50),
        year INT,
        branch VARCHAR(100),
        sec VARCHAR(50),
        tools VARCHAR(255),
        technologies VARCHAR(255),
        status VARCHAR(20) DEFAULT 'pending',
        student_id INT,
        approved_by INT,
        faculty_remarks TEXT,
        submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        reviewed_at DATETIME
    );
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(text(users_sql))
            conn.execute(text(submissions_sql))
            conn.commit()
            print("Authentication tables created successfully")
    except Exception as e:
        print(f"Table creation warning: {e}")

if __name__ == "__main__":
    create_auth_tables()