# main_auth.py - Full authentication version
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
import models, schemas
from database import SessionLocal, engine, Base, get_db
import os

# Auth setup
SECRET_KEY = os.getenv("SECRET_KEY", "mits-college-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Auth Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

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
    status = Column(String(20), default="pending")
    student_id = Column(Integer)
    approved_by = Column(Integer)
    faculty_remarks = Column(Text)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)

# Auth Schemas
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class ProjectSubmissionCreate(BaseModel):
    project_name: str
    idea: str
    team_members: str = None
    roll_number: str = None
    class_name: str = None
    year: int = None
    branch: str = None
    sec: str = None
    tools: str = None
    technologies: str = None

# Create tables
try:
    Base.metadata.create_all(bind=engine)
except:
    pass

app = FastAPI(title="Project Scope - Full Stack")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=403, detail=f"Access denied. Required role: {required_role}")
        return current_user
    return role_checker

# Routes
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Project Scope Backend is running"}

@app.get("/")
async def read_index():
    return FileResponse('frontend.html')

@app.get("/simple")
async def read_simple():
    return FileResponse('index.html')

# Auth endpoints
@app.post("/auth/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate college email
    if not user.email.endswith("@mits.ac.in"):
        raise HTTPException(status_code=400, detail="Only MITS college emails allowed")
    
    # Create user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User registered successfully", "user_id": db_user.id}

@app.post("/auth/login", response_model=Token)
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

@app.get("/auth/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role
    }

# Student endpoints
@app.post("/submissions/")
def submit_project(project: ProjectSubmissionCreate, current_user: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    db_submission = ProjectSubmission(**project.dict(), student_id=current_user.id)
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return {"message": "Project submitted successfully", "id": db_submission.id}

# Faculty endpoints
@app.get("/submissions/")
def get_submissions(current_user: User = Depends(require_role("faculty")), db: Session = Depends(get_db)):
    return db.query(ProjectSubmission).all()

@app.put("/submissions/{submission_id}")
def review_submission(submission_id: int, status: str, remarks: str = "", current_user: User = Depends(require_role("faculty")), db: Session = Depends(get_db)):
    submission = db.query(ProjectSubmission).filter(ProjectSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    submission.status = status
    submission.faculty_remarks = remarks
    submission.approved_by = current_user.id
    submission.reviewed_at = datetime.utcnow()
    
    # If approved, create project
    if status == "approved":
        project_data = {
            "project_name": submission.project_name,
            "idea": submission.idea,
            "team_members": submission.team_members,
            "roll_number": submission.roll_number,
            "class_name": submission.class_name,
            "year": submission.year,
            "branch": submission.branch,
            "sec": submission.sec,
            "tools": submission.tools,
            "technologies": submission.technologies
        }
        db_project = models.Project(**project_data)
        db.add(db_project)
    
    db.commit()
    return {"message": "Submission reviewed successfully"}

# Project endpoints (public for backward compatibility)
@app.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    data = project.dict()
    for fld in ("team_members", "tools", "technologies"):
        val = data.get(fld)
        if isinstance(val, (list, tuple)):
            data[fld] = ",".join(map(str, val))

    db_project = models.Project(**data)
    db.add(db_project)
    try:
        db.commit()
        db.refresh(db_project)
        return db_project
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/")
def get_projects(db: Session = Depends(get_db)):
    try:
        return db.query(models.Project).all()
    except:
        return []

@app.get("/projects/search")
def search_projects(q: str = "", current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if q:
        projects = db.query(models.Project).filter(
            models.Project.project_name.contains(q) |
            models.Project.tools.contains(q) |
            models.Project.technologies.contains(q)
        ).all()
    else:
        projects = db.query(models.Project).all()
    return projects

@app.get("/projects/{project_id}", response_model=schemas.Project)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, updated_project: schemas.ProjectCreate, current_user: User = Depends(require_role("faculty")), db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in updated_project.dict().items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project

@app.delete("/projects/{project_id}")
def delete_project(project_id: int, current_user: User = Depends(require_role("faculty")), db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"detail": "Project deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)