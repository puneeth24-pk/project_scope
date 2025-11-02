# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import models, schemas, auth_models, auth_schemas
from database import SessionLocal, engine, Base, get_db
from auth import authenticate_user, create_access_token, get_current_user, require_role, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    # Also create auth tables manually for safety
    from startup import create_auth_tables
    create_auth_tables()
except Exception as e:
    print(f"Database setup warning: {e}")
    # Continue anyway for backward compatibility

app = FastAPI(title="Project Scope Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Project Scope Backend is running"}

# API status endpoint
@app.get("/api/status")
def api_status():
    return {"api": "online", "version": "1.0", "endpoints": ["/projects/", "/health"]}

# Serve the simple frontend at root (no auth required)
@app.get("/")
async def read_index():
    return FileResponse('frontend_simple.html')

# Serve auth frontend
@app.get("/auth")
async def read_auth():
    return FileResponse('frontend.html')

# Serve old simple form for testing
@app.get("/simple")
async def read_simple():
    return FileResponse('index.html')

# AUTH ENDPOINTS
@app.post("/auth/register")
def register_user(user: auth_schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user exists
        db_user = db.query(auth_models.User).filter(auth_models.User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Validate college email
        if not user.email.endswith("@mits.ac.in"):
            raise HTTPException(status_code=400, detail="Only MITS college emails allowed")
        
        # Create user
        hashed_password = get_password_hash(user.password)
        db_user = auth_models.User(
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name,
            role=user.role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"message": "User registered successfully", "user_id": db_user.id}
    except Exception as e:
        db.rollback()
        # If auth tables don't exist, create them
        try:
            from startup import create_auth_tables
            create_auth_tables()
            return {"message": "Database initialized. Please try registration again."}
        except:
            raise HTTPException(status_code=500, detail="Database setup required. Please contact admin.")

@app.post("/auth/login", response_model=auth_schemas.Token)
def login_user(user_credentials: auth_schemas.UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@app.get("/auth/me", response_model=auth_schemas.User)
def read_users_me(current_user: auth_models.User = Depends(get_current_user)):
    return current_user



# STUDENT: Submit project for approval
@app.post("/submissions/", response_model=auth_schemas.ProjectSubmission)
def submit_project(project: auth_schemas.ProjectSubmissionCreate, current_user: auth_models.User = Depends(require_role("student")), db: Session = Depends(get_db)):
    db_submission = auth_models.ProjectSubmission(**project.dict(), student_id=current_user.id)
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

# FACULTY: Get all submissions
@app.get("/submissions/")
def get_submissions(current_user: auth_models.User = Depends(require_role("faculty")), db: Session = Depends(get_db)):
    return db.query(auth_models.ProjectSubmission).all()

# FACULTY: Approve/Reject submission
@app.put("/submissions/{submission_id}")
def review_submission(submission_id: int, review: auth_schemas.ProjectSubmissionUpdate, current_user: auth_models.User = Depends(require_role("faculty")), db: Session = Depends(get_db)):
    submission = db.query(auth_models.ProjectSubmission).filter(auth_models.ProjectSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    submission.status = review.status
    submission.faculty_remarks = review.faculty_remarks
    submission.approved_by = current_user.id
    submission.reviewed_at = datetime.utcnow()
    
    # If approved, create project
    if review.status == "approved":
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

# FACULTY: Add project directly (with auth) OR Public endpoint (without auth)
@app.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    # Allow both authenticated faculty and public access for backward compatibility
    # Coerce list/tuple fields to comma-separated strings to avoid DB type errors
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
        # Roll back and surface the error (include traceback for local debugging)
        db.rollback()
        import traceback
        tb = traceback.format_exc()
        # Return a clear HTTP 500 with exception message and traceback to help debug locally.
        raise HTTPException(status_code=500, detail=f"{e}\n{tb}")

# PUBLIC: Search projects (available to all authenticated users)
@app.get("/projects/search")
def search_projects(q: str = "", current_user: auth_models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if q:
        projects = db.query(models.Project).filter(
            models.Project.project_name.contains(q) |
            models.Project.tools.contains(q) |
            models.Project.technologies.contains(q)
        ).all()
    else:
        projects = db.query(models.Project).all()
    return projects

# READ: Get all projects (public for backward compatibility)
@app.get("/projects/")
def get_projects(db: Session = Depends(get_db)):
    try:
        return db.query(models.Project).all()
    except Exception as e:
        return []

# READ: Get a project by ID
@app.get("/projects/{project_id}", response_model=schemas.Project)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# UPDATE: Update a project by ID (public for backward compatibility)
@app.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, updated_project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in updated_project.dict().items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project

# DELETE: Delete a project by ID (public for backward compatibility)
@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"detail": "Project deleted successfully"}

# DESCRIBE: Get project table structure
@app.get("/projects/describe")
def describe_projects(db: Session = Depends(get_db)):
    # This is a raw SQL query to get the table structure
    result = db.execute("DESCRIBE projects")
    return {"columns": [dict(row) for row in result]}

# READ: Get first 10 projects (for testing/querying)
@app.get("/projects/sample")
def get_sample_projects(db: Session = Depends(get_db)):
    # This is a raw SQL query to get a sample of 10 projects
    result = db.execute("SELECT * FROM projects LIMIT 10")
    return {"sample_projects": [dict(row) for row in result]}

# DROP: Delete the entire projects table (use with caution!)
@app.delete("/projects/drop")
def drop_projects(db: Session = Depends(get_db)):
    # This will drop the projects table and all its data
    db.execute("DROP TABLE IF EXISTS projects")
    db.commit()
    return {"detail": "Projects table dropped successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
