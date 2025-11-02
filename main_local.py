# main_local.py - Works without database for local testing
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import os

app = FastAPI(title="Project Scope - Local")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for local testing
projects_data = []
next_id = 1

class ProjectCreate(BaseModel):
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

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Local server running"}

@app.get("/")
async def read_index():
    return FileResponse('frontend_simple.html')

@app.get("/simple")
async def read_simple():
    return FileResponse('index.html')

@app.post("/projects/")
def create_project(project: ProjectCreate):
    global next_id
    project_dict = project.dict()
    project_dict["id"] = next_id
    projects_data.append(project_dict)
    next_id += 1
    return project_dict

@app.get("/projects/")
def get_projects():
    return projects_data

@app.get("/projects/{project_id}")
def get_project(project_id: int):
    for project in projects_data:
        if project["id"] == project_id:
            return project
    return {"error": "Project not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)