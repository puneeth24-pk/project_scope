# schemas.py
from pydantic import BaseModel

class ProjectBase(BaseModel):
    project_name: str
    idea: str
    team_members: str | None = None
    roll_number: str | None = None
    class_name: str | None = None
    year: int | None = None
    branch: str | None = None
    sec: str | None = None
    tools: str | None = None
    technologies: str | None = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int

    class Config:
        from_attributes = True  # Pydantic v2 replacement for orm_mode
