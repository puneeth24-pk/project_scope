# schemas.py
from pydantic import BaseModel
from typing import Optional

class ProjectCreate(BaseModel):
    project_name: str
    idea: Optional[str] = None
    team_members: Optional[str] = None
    roll_number: Optional[str] = None
    class_name: Optional[str] = None
    year: Optional[str] = None
    branch: Optional[str] = None
    section: Optional[str] = None
    tools: Optional[str] = None

class ProjectUpdate(BaseModel):
    project_name: Optional[str]
    idea: Optional[str]
    team_members: Optional[str]
    roll_number: Optional[str]
    class_name: Optional[str]
    year: Optional[str]
    branch: Optional[str]
    section: Optional[str]
    tools: Optional[str]

class ProjectOut(BaseModel):
    id: int
    project_name: str
    idea: Optional[str] = None
    team_members: Optional[str] = None
    roll_number: Optional[str] = None
    class_name: Optional[str] = None
    year: Optional[str] = None
    branch: Optional[str] = None
    section: Optional[str] = None
    tools: Optional[str] = None

    class Config:
        orm_mode = True
