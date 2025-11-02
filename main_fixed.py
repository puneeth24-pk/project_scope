# main_fixed.py - Fixed database connection with fallback
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas
import os

# Try to connect to database, fallback to in-memory if fails
try:
    from database import SessionLocal, engine, Base, get_db
    Base.metadata.create_all(bind=engine)
    USE_DATABASE = True
    print("✅ Database connected successfully")
except Exception as e:
    print(f"⚠️ Database connection failed: {e}")
    print("🔄 Using in-memory storage for local testing")
    USE_DATABASE = False
    
    # In-memory fallback
    projects_data = []
    next_id = 1
    
    def get_db():
        return None

app = FastAPI(title="Project Scope Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    db_status = "connected" if USE_DATABASE else "in-memory"
    return {"status": "healthy", "database": db_status}

@app.get("/")
async def read_index():
    return FileResponse('frontend_simple.html')

@app.get("/simple")
async def read_simple():
    return FileResponse('index.html')

@app.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    if USE_DATABASE:
        # Database version
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
    else:
        # In-memory version
        global next_id
        project_dict = project.dict()
        project_dict["id"] = next_id
        projects_data.append(project_dict)
        next_id += 1
        return project_dict

@app.get("/projects/")
def get_projects(db: Session = Depends(get_db)):
    if USE_DATABASE:
        try:
            projects = db.query(models.Project).all()
            return projects
        except:
            return []
    else:
        return projects_data

@app.get("/projects/{project_id}", response_model=schemas.Project)
def get_project(project_id: int, db: Session = Depends(get_db)):
    if USE_DATABASE:
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    else:
        for project in projects_data:
            if project["id"] == project_id:
                return project
        raise HTTPException(status_code=404, detail="Project not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)