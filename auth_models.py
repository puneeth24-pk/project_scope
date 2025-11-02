# auth_models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # 'student' or 'faculty'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    submitted_projects = relationship("ProjectSubmission", back_populates="student")
    approved_projects = relationship("ProjectSubmission", foreign_keys="ProjectSubmission.approved_by", back_populates="faculty")

class ProjectSubmission(Base):
    __tablename__ = "project_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255), nullable=False)
    idea = Column(Text, nullable=False)
    team_members = Column(String(255))
    roll_number = Column(String(50))
    class_name = Column(String(50))
    year = Column(Integer)
    branch = Column(String(100))
    sec = Column(String(50))
    tools = Column(String(255))
    technologies = Column(String(255))
    
    # Status and approval
    status = Column(String(20), default="pending")  # 'pending', 'approved', 'rejected'
    student_id = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    faculty_remarks = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Relationships
    student = relationship("User", foreign_keys=[student_id], back_populates="submitted_projects")
    faculty = relationship("User", foreign_keys=[approved_by], back_populates="approved_projects")