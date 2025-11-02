# main_simple.py - Simplified version that works
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine, Base, get_db

# Create tables
try:
    Base.metadata.create_all(bind=engine)
except:
    pass

app = FastAPI(title="Project Scope Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Project Scope Backend is running"}

# Serve frontend
@app.get("/")
async def read_index():
    return FileResponse('frontend.html')

@app.get("/simple")
async def read_simple():
    return FileResponse('index.html')

# CREATE: Add new project
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

# READ: Get all projects
@app.get("/projects/")
def get_projects(db: Session = Depends(get_db)):
    try:
        projects = db.query(models.Project).all()
        return projects
    except:
        return []

# READ: Get project by ID
@app.get("/projects/{project_id}", response_model=schemas.Project)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# UPDATE: Update project
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

# DELETE: Delete project
@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"detail": "Project deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)