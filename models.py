# models.py
from sqlalchemy import Column, Integer, String
from database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255), nullable=False)
    idea = Column(String(500), nullable=False)
    team_members = Column(String(255))
    roll_number = Column(String(50))
    class_name = Column(String(50))
    year = Column(Integer)
    branch = Column(String(100))
    sec = Column(String(50))
    tools = Column(String(255))
    technologies = Column(String(255))
