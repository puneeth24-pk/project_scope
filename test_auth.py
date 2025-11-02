#!/usr/bin/env python3
"""
Test script for authentication system
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"  # Change to your deployed URL
TEST_EMAIL = "test.student@mits.ac.in"
TEST_PASSWORD = "testpass123"
FACULTY_EMAIL = "test.faculty@mits.ac.in"

def test_registration():
    """Test user registration"""
    print("🔐 Testing Registration...")
    
    # Test student registration
    student_data = {
        "full_name": "Test Student",
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "role": "student"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=student_data)
    print(f"Student Registration: {response.status_code}")
    if response.status_code == 200:
        print("✅ Student registered successfully")
    else:
        print(f"❌ Student registration failed: {response.text}")
    
    # Test faculty registration
    faculty_data = {
        "full_name": "Test Faculty",
        "email": FACULTY_EMAIL,
        "password": TEST_PASSWORD,
        "role": "faculty"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=faculty_data)
    print(f"Faculty Registration: {response.status_code}")
    if response.status_code == 200:
        print("✅ Faculty registered successfully")
    else:
        print(f"❌ Faculty registration failed: {response.text}")

def test_login():
    """Test user login"""
    print("\n🔑 Testing Login...")
    
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful")
        print(f"Token: {data['access_token'][:20]}...")
        print(f"User: {data['user']['full_name']} ({data['user']['role']})")
        return data['access_token']
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_protected_endpoint(token):
    """Test protected endpoint access"""
    print("\n🛡️ Testing Protected Endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    print(f"Protected Endpoint Status: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        print("✅ Protected endpoint access successful")
        print(f"User Info: {user_data['full_name']} - {user_data['email']}")
    else:
        print(f"❌ Protected endpoint access failed: {response.text}")

def test_project_submission(token):
    """Test project submission (student)"""
    print("\n📝 Testing Project Submission...")
    
    project_data = {
        "project_name": "Test AI Project",
        "idea": "An AI-powered project management system",
        "team_members": "Test Student, Another Student",
        "roll_number": "21CS001",
        "class_name": "CSE-A",
        "year": 2024,
        "branch": "Computer Science",
        "sec": "A",
        "tools": "Python, FastAPI, React",
        "technologies": "Machine Learning, Web Development"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/submissions/", json=project_data, headers=headers)
    
    print(f"Project Submission Status: {response.status_code}")
    if response.status_code == 200:
        submission = response.json()
        print("✅ Project submitted successfully")
        print(f"Submission ID: {submission['id']}")
        return submission['id']
    else:
        print(f"❌ Project submission failed: {response.text}")
        return None

def test_health_check():
    """Test health check endpoint"""
    print("🏥 Testing Health Check...")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Backend is healthy")
        print(f"Response: {response.json()}")
    else:
        print("❌ Backend health check failed")

def main():
    """Run all tests"""
    print("🚀 Starting Authentication System Tests")
    print("=" * 50)
    
    # Test health check first
    test_health_check()
    
    # Test registration
    test_registration()
    
    # Test login
    token = test_login()
    
    if token:
        # Test protected endpoints
        test_protected_endpoint(token)
        
        # Test project submission
        submission_id = test_project_submission(token)
        
        if submission_id:
            print(f"\n✅ All tests completed! Submission ID: {submission_id}")
        else:
            print("\n⚠️ Some tests failed")
    else:
        print("\n❌ Login failed, skipping protected endpoint tests")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("- Registration: Check console output")
    print("- Login: Check console output") 
    print("- Protected Access: Check console output")
    print("- Project Submission: Check console output")

if __name__ == "__main__":
    main()