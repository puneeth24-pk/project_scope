# auth_schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class ProjectSubmissionBase(BaseModel):
    project_name: str
    idea: str
    team_members: Optional[str] = None
    roll_number: Optional[str] = None
    class_name: Optional[str] = None
    year: Optional[int] = None
    branch: Optional[str] = None
    sec: Optional[str] = None
    tools: Optional[str] = None
    technologies: Optional[str] = None

class ProjectSubmissionCreate(ProjectSubmissionBase):
    pass

class ProjectSubmissionUpdate(BaseModel):
    status: str
    faculty_remarks: Optional[str] = None

class ProjectSubmission(ProjectSubmissionBase):
    id: int
    status: str
    student_id: int
    approved_by: Optional[int] = None
    faculty_remarks: Optional[str] = None
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True