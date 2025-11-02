# 🚀 Render Deployment Guide - Project Scope

## 📋 Prerequisites
- GitHub repository with the project code
- Render account (free tier available)
- MySQL database (Railway/PlanetScale/Render PostgreSQL)

## 🔧 Backend Deployment on Render

### Step 1: Create Web Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `projectscope-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

### Step 2: Environment Variables
Add these environment variables in Render:
```
SECRET_KEY=your-secret-key-here
MYSQL_USER=your-mysql-username
MYSQL_PASSWORD=your-mysql-password
MYSQL_HOST=your-mysql-host
MYSQL_DB=your-database-name
MYSQL_PORT=3306
```

### Step 3: Deploy
- Click "Create Web Service"
- Wait for deployment to complete
- Note your backend URL: `https://projectscope-backend.onrender.com`

## 🌐 Frontend Deployment on Render

### Option 1: Static Site (Recommended)
1. Click "New +" → "Static Site"
2. Connect same GitHub repository
3. Configure:
   - **Build Command**: Leave empty (static HTML)
   - **Publish Directory**: `.` (root directory)
4. The frontend will be available at: `https://projectscope.onrender.com`

### Option 2: Serve from Backend
The backend already serves the frontend at the root URL, so you can use the same backend URL for both API and frontend.

## 🔐 Authentication Features Included

### ✅ User Registration & Login
- College email validation (@mits.ac.in)
- JWT token-based authentication
- Role-based access (Student/Faculty)

### ✅ Student Features
- Search existing projects
- Submit project ideas for approval
- View project details and similar projects

### ✅ Faculty Features
- Review and approve/reject student submissions
- Add projects directly
- Manage existing projects
- Add remarks and feedback

## 🗄️ Database Schema

The application will automatically create these tables:

### Users Table
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Project Submissions Table
```sql
CREATE TABLE project_submissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_name VARCHAR(255) NOT NULL,
    idea TEXT NOT NULL,
    team_members VARCHAR(255),
    roll_number VARCHAR(50),
    class_name VARCHAR(50),
    year INT,
    branch VARCHAR(100),
    sec VARCHAR(50),
    tools VARCHAR(255),
    technologies VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    student_id INT,
    approved_by INT,
    faculty_remarks TEXT,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed_at DATETIME,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);
```

## 🧪 Testing the Deployment

### 1. Test Authentication
- Visit your deployed frontend URL
- Register a student account with @mits.ac.in email
- Register a faculty account
- Test login functionality

### 2. Test Student Features
- Login as student
- Search for projects
- Submit a new project idea

### 3. Test Faculty Features
- Login as faculty
- Review pending submissions
- Approve/reject submissions
- Add new projects directly

## 📱 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user

### Projects (Faculty only)
- `GET /projects/` - Get all projects
- `POST /projects/` - Add new project
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

### Project Search (All authenticated users)
- `GET /projects/search?q=query` - Search projects

### Submissions (Students & Faculty)
- `POST /submissions/` - Submit project (Students)
- `GET /submissions/` - Get all submissions (Faculty)
- `PUT /submissions/{id}` - Review submission (Faculty)

## 🔒 Security Features

- JWT token authentication
- Password hashing with bcrypt
- Role-based access control
- College email validation
- CORS configuration for cross-origin requests

## 🎯 Live URLs

After deployment, you'll have:
- **Backend API**: `https://projectscope-backend.onrender.com`
- **Frontend**: `https://projectscope.onrender.com` (or same as backend)
- **API Docs**: `https://projectscope-backend.onrender.com/docs`

## 🚨 Important Notes

1. **Free Tier Limitations**: Render free tier may have cold starts
2. **Database**: Ensure your MySQL database is accessible from Render
3. **Environment Variables**: Never commit sensitive data to GitHub
4. **HTTPS**: Render provides HTTPS by default
5. **Domain**: You can add a custom domain in Render settings

## 🔧 Troubleshooting

### Common Issues:
1. **Database Connection**: Check environment variables
2. **CORS Errors**: Ensure frontend URL is in CORS origins
3. **Authentication**: Verify JWT secret key is set
4. **Email Validation**: Only @mits.ac.in emails are allowed

### Logs:
- Check Render logs for deployment issues
- Use `/health` endpoint to verify backend status
- Test API endpoints using `/docs` (Swagger UI)

---

**🎉 Your full-stack Project Scope application is now deployed and ready to use!**