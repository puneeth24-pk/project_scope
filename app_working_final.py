# app_working_final.py - Fixed bcrypt issue
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import hashlib
import secrets
from jose import jwt
from pydantic import BaseModel
from datetime import datetime, timedelta
import os

# Database connection
DATABASE_URL = "mysql+pymysql://root:OxlvxnNzxEsnhhqBMAgurtxZnNSEctru@maglev.proxy.rlwy.net:27275/railway"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
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

# Simple password hashing (avoiding bcrypt issues)
SECRET_KEY = "mits-college-secret-key"

def hash_password(password: str) -> str:
    """Simple password hashing using SHA256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        salt, password_hash = hashed.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except:
        return False

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

# FastAPI app
app = FastAPI(title="Project Scope - MITS College")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Project Scope Backend Running"}

@app.get("/")
async def home():
    return FileResponse('main_page.html')

@app.get("/student")
async def student_page():
    return FileResponse('student_page.html')

@app.get("/faculty")
async def faculty_page():
    return FileResponse('faculty_page.html')

@app.get("/student/dashboard")
async def student_dashboard():
    return FileResponse('student_dash.html')

@app.get("/faculty/dashboard")
async def faculty_dashboard():
    return FileResponse('faculty_dash.html')

# Auth endpoints
@app.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user exists
        result = db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": user.email})
        if result.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Validate MITS email
        if not user.email.endswith("@mits.ac.in"):
            raise HTTPException(status_code=400, detail="Only @mits.ac.in emails allowed")
        
        # Create user with simple password hashing
        hashed_password = hash_password(user.password)
        db.execute(text("""
            INSERT INTO users (email, hashed_password, full_name, role, is_active, created_at) 
            VALUES (:email, :password, :name, :role, 1, NOW())
        """), {
            "email": user.email,
            "password": hashed_password,
            "name": user.full_name,
            "role": user.role
        })
        db.commit()
        return {"message": "Registration successful"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/auth/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    try:
        # Get user
        result = db.execute(text("""
            SELECT id, email, hashed_password, full_name, role 
            FROM users WHERE email = :email
        """), {"email": credentials.email})
        
        user_row = result.fetchone()
        if not user_row:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not verify_password(credentials.password, user_row.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create token
        token = create_access_token(data={"sub": user_row.email, "role": user_row.role})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "email": user_row.email,
                "full_name": user_row.full_name,
                "role": user_row.role
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

# Project endpoints
@app.post("/projects/")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    try:
        db.execute(text("""
            INSERT INTO projects (project_name, idea, team_members, roll_number, class_name, 
                                year, branch, sec, tools, technologies) 
            VALUES (:name, :idea, :team, :roll, :class, :year, :branch, :sec, :tools, :tech)
        """), {
            "name": project.project_name,
            "idea": project.idea,
            "team": project.team_members,
            "roll": project.roll_number,
            "class": project.class_name,
            "year": project.year,
            "branch": project.branch,
            "sec": project.sec,
            "tools": project.tools,
            "tech": project.technologies
        })
        db.commit()
        
        result = db.execute(text("SELECT LAST_INSERT_ID()"))
        project_id = result.fetchone()[0]
        
        return {"id": project_id, "message": "Project created successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

@app.get("/projects/")
def get_projects(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT * FROM projects ORDER BY id DESC"))
        projects = []
        for row in result:
            projects.append({
                "id": row.id,
                "project_name": row.project_name,
                "idea": row.idea,
                "team_members": row.team_members,
                "roll_number": row.roll_number,
                "class_name": row.class_name,
                "year": row.year,
                "branch": row.branch,
                "sec": row.sec,
                "tools": row.tools,
                "technologies": row.technologies
            })
        return projects
    except Exception as e:
        return []

@app.get("/projects/search")
def search_projects(q: str = "", db: Session = Depends(get_db)):
    try:
        if q:
            result = db.execute(text("""
                SELECT * FROM projects 
                WHERE project_name LIKE :query 
                   OR tools LIKE :query 
                   OR technologies LIKE :query
                ORDER BY id DESC
            """), {"query": f"%{q}%"})
        else:
            result = db.execute(text("SELECT * FROM projects ORDER BY id DESC"))
        
        projects = []
        for row in result:
            projects.append({
                "id": row.id,
                "project_name": row.project_name,
                "idea": row.idea,
                "team_members": row.team_members,
                "roll_number": row.roll_number,
                "class_name": row.class_name,
                "year": row.year,
                "branch": row.branch,
                "sec": row.sec,
                "tools": row.tools,
                "technologies": row.technologies
            })
        return projects
    except Exception as e:
        return []

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)