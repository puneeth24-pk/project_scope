# models.py
from sqlalchemy import Column, Integer, String, Text
from database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255), nullable=False)
    idea = Column(Text, nullable=True)
    team_members = Column(String(255), nullable=True)
    roll_number = Column(String(255), nullable=True)
    class_name = Column(String(100), nullable=True)
    year = Column(String(50), nullable=True)
    branch = Column(String(100), nullable=True)
    section = Column(String(50), nullable=True)
    tools = Column(String(255), nullable=True)
