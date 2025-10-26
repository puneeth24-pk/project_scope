# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal, engine, Base
import models, schemas

# Create tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Project Submission API")

# CORS for Streamlit access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace "*" with your Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CREATE project
@app.post("/projects/", response_model=schemas.ProjectOut)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = models.Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

# READ all projects
@app.get("/projects/", response_model=List[schemas.ProjectOut])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    return projects

# READ single project
@app.get("/projects/{project_id}", response_model=schemas.ProjectOut)
def read_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# UPDATE project
@app.put("/projects/{project_id}", response_model=schemas.ProjectOut)
def update_project(project_id: int, project_update: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in project_update.dict(exclude_unset=True).items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project

# DELETE project
@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"detail": "Project deleted"}
