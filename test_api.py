import requests
import json

# Test the deployed backend
API_URL = "https://projscopebackend.onrender.com"

def test_backend():
    print("Testing Project Scope Backend...")
    
    # Test health check
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        print(f"Health Check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return False
    
    # Test get projects
    try:
        response = requests.get(f"{API_URL}/projects/", timeout=10)
        print(f"Get Projects: {response.status_code}")
        if response.ok:
            projects = response.json()
            print(f"Found {len(projects)} projects")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Get projects failed: {e}")
        return False
    
    # Test create project
    try:
        test_data = {
            "project_name": "Test Project",
            "idea": "Test idea for API testing",
            "team_members": "Test Team",
            "roll_number": "TEST123",
            "class_name": "Test Class",
            "year": 2024,
            "branch": "CS",
            "sec": "A",
            "tools": "Python",
            "technologies": "FastAPI"
        }
        
        response = requests.post(f"{API_URL}/projects/", 
                               json=test_data, 
                               headers={"Content-Type": "application/json"},
                               timeout=10)
        print(f"Create Project: {response.status_code}")
        if response.ok:
            project = response.json()
            print(f"Created project with ID: {project['id']}")
            return project['id']
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Create project failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_backend()