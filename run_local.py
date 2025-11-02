#!/usr/bin/env python3
"""
Simple local server that definitely works
"""
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Project Scope - Local")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage
projects = []
next_id = 1

class Project(BaseModel):
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

@app.get("/")
async def home():
    return FileResponse('frontend_simple.html')

@app.get("/health")
def health():
    return {"status": "healthy", "message": "Local backend running", "projects_count": len(projects)}

@app.post("/projects/")
def create_project(project: Project):
    global next_id
    project_data = project.dict()
    project_data["id"] = next_id
    projects.append(project_data)
    next_id += 1
    print(f"Project created: {project_data['project_name']} (ID: {project_data['id']})")
    return project_data
    return project_data

@app.get("/projects/")
def get_projects():
    return projects

if __name__ == "__main__":
    import uvicorn
    print("Starting Project Scope Local Server...")
    print("Frontend: http://localhost:8003")
    print("API Docs: http://localhost:8003/docs")
    print("Health: http://localhost:8003/health")
    uvicorn.run(app, host="127.0.0.1", port=8003)