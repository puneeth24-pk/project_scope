# main_final.py - Uses only existing projects and users tables
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean, DateTime
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

app = FastAPI(title="Project Scope - MITS College")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Users table model (existing)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # 'student' or 'faculty'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Schemas
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
    return {"status": "healthy", "message": "Project Scope - Using existing tables"}

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

# Search projects (all authenticated users)
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

# Faculty: Add project directly to projects table
@app.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, current_user: User = Depends(require_role("faculty")), db: Session = Depends(get_db)):
    data = project.dict()
    for fld in ("team_members", "tools", "technologies"):
        val = data.get(fld)
        if isinstance(val, (list, tuple)):
            data[fld] = ",".join(map(str, val))

    db_project = models.Project(**data)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

# Students: Submit project idea (stored in projects table with pending status)
@app.post("/submissions/")
def submit_project_idea(project: schemas.ProjectCreate, current_user: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    data = project.dict()
    # Add student info and pending status
    data["team_members"] = f"Submitted by: {current_user.full_name} | " + (data.get("team_members") or "")
    data["tools"] = (data.get("tools") or "") + f" | Status: PENDING_APPROVAL"
    
    db_project = models.Project(**data)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return {"message": "Project idea submitted for approval", "id": db_project.id}

# Faculty: Get all projects (including pending ones)
@app.get("/projects/")
def get_projects(current_user: User = Depends(require_role("faculty")), db: Session = Depends(get_db)):
    return db.query(models.Project).all()

# Faculty: Get pending submissions
@app.get("/submissions/")
def get_pending_submissions(current_user: User = Depends(require_role("faculty")), db: Session = Depends(get_db)):
    # Get projects with PENDING_APPROVAL in tools field
    pending = db.query(models.Project).filter(models.Project.tools.contains("PENDING_APPROVAL")).all()
    return pending

# Faculty: Approve/Reject submission
@app.put("/projects/{project_id}/review")
def review_project(project_id: int, action: str, remarks: str = "", current_user: User = Depends(require_role("faculty")), db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if action == "approve":
        # Remove pending status
        project.tools = project.tools.replace(" | Status: PENDING_APPROVAL", "")
        project.tools += f" | Approved by: {current_user.full_name}"
    elif action == "reject":
        # Mark as rejected
        project.tools = project.tools.replace("PENDING_APPROVAL", "REJECTED")
        project.tools += f" | Rejected by: {current_user.full_name}"
    
    if remarks:
        project.tools += f" | Remarks: {remarks}"
    
    db.commit()
    return {"message": f"Project {action}ed successfully"}

# Faculty: Update project
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

# Faculty: Delete project
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