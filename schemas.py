# schemas.py
from pydantic import BaseModel

class ProjectBase(BaseModel):
    project_name: str
    idea: str
    # Accept either a string or a list of strings from clients; we'll coerce lists to comma-strings server-side
    team_members: str | list[str] | None = None
    roll_number: str | None = None
    class_name: str | None = None
    year: int | None = None
    branch: str | None = None
    sec: str | None = None
    tools: str | list[str] | None = None
    technologies: str | list[str] | None = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int

    class Config:
        from_attributes = True  # Pydantic v2 replacement for orm_mode
