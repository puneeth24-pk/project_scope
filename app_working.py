# app_working.py - Simple working version without relationship issues
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from jose import jwt
from pydantic import BaseModel
from datetime import datetime, timedelta
import os

# Database setup
MYSQL_USER = "root"
MYSQL_PASSWORD = "OxlvxnNzxEsnhhqBMAgurtxZnNSEctru"
MYSQL_HOST = "maglev.proxy.rlwy.net"
MYSQL_DB = "railway"
MYSQL_PORT = "27275"

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simple Models (no relationships to avoid errors)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

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

# Schemas
class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    role: str

class UserLogin(BaseModel):
    email: str
    password: str

class ProjectCreate(BaseModel):
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

# Auth setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "mits-college-secret-key"

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

# FastAPI app
app = FastAPI(title="Project Scope")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

# Main page - choose role
@app.get("/")
async def home():
    return FileResponse('login_page.html')

# Student login page
@app.get("/student")
async def student_page():
    return FileResponse('student_login.html')

# Faculty login page  
@app.get("/faculty")
async def faculty_page():
    return FileResponse('faculty_login.html')

# Student dashboard (after login)
@app.get("/student/dashboard")
async def student_dashboard():
    return FileResponse('student_dashboard.html')

# Faculty dashboard (after login)
@app.get("/faculty/dashboard")
async def faculty_dashboard():
    return FileResponse('faculty_dashboard.html')

# Auth endpoints
@app.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate MITS email
    if not user.email.endswith("@mits.ac.in"):
        raise HTTPException(status_code=400, detail="Only @mits.ac.in emails allowed")
    
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
    return {"message": "Registration successful"}

@app.post("/auth/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(data={"sub": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

# Project endpoints
@app.post("/projects/")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/projects/")
def get_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()

@app.get("/projects/search")
def search_projects(q: str = "", db: Session = Depends(get_db)):
    if q:
        projects = db.query(Project).filter(
            Project.project_name.contains(q) |
            Project.tools.contains(q) |
            Project.technologies.contains(q)
        ).all()
    else:
        projects = db.query(Project).all()
    return projects

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)