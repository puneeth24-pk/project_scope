# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

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

# Serve the HTML form at root
@app.get("/")
async def read_index():
    return FileResponse('index.html')

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CREATE: Add new project
@app.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
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

# READ: Get all projects
@app.get("/projects/", response_model=list[schemas.Project])
def get_projects(db: Session = Depends(get_db)):
    try:
        projects = db.query(models.Project).all()
        return projects
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}\n{tb}")

# READ: Get a project by ID
@app.get("/projects/{project_id}", response_model=schemas.Project)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# UPDATE: Update a project by ID
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

# DELETE: Delete a project by ID
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
