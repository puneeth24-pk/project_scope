# 🚀 Project Scope - Full Stack Web Application

A comprehensive project management and submission system with authentication, role-based access, and modern UI built for MITS College.

## 🌟 Features

### 🔐 Authentication System
- **User Registration & Login**: JWT-based authentication
- **Role-Based Access**: Student and Faculty roles with different permissions
- **College Email Validation**: Only @mits.ac.in emails allowed
- **Secure Password Hashing**: bcrypt encryption

### 👨‍🎓 Student Features
- **Project Search**: Search existing projects by name, tools, or technologies
- **Project Submission**: Submit project ideas for faculty approval
- **Duplicate Detection**: Check if similar projects already exist
- **View Project Details**: See tools, technologies, and team information

### 👩‍🏫 Faculty Features
- **Review Submissions**: Approve or reject student project ideas
- **Add Projects Directly**: Create projects without approval process
- **Manage Projects**: Edit and delete existing projects
- **Add Remarks**: Provide feedback on submissions
- **Dashboard**: View all pending submissions and approved projects

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **PyMySQL**: MySQL database connector
- **JWT**: JSON Web Tokens for authentication
- **Passlib**: Password hashing with bcrypt
- **Pydantic**: Data validation and serialization

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **Vanilla JavaScript**: No framework dependencies
- **Font Awesome**: Icon library
- **CSS Grid/Flexbox**: Layout system

### Database
- **MySQL**: Primary database
- **Railway/Render**: Cloud database hosting

### Deployment
- **Render**: Full-stack deployment platform
- **Docker**: Containerization support
- **GitHub**: Version control and CI/CD

## 📁 Project Structure

```
project1/
├── main.py                    # FastAPI application with all endpoints
├── models.py                  # Original project models
├── auth_models.py             # Authentication and submission models
├── schemas.py                 # Original Pydantic schemas
├── auth_schemas.py            # Authentication schemas
├── auth.py                    # JWT authentication utilities
├── database.py                # Database configuration
├── frontend.html              # Modern authentication-enabled frontend
├── index.html                 # Simple project submission form
├── requirements.txt           # Python dependencies
├── render.yaml               # Render deployment configuration
├── Dockerfile                # Docker containerization
├── deployment_guide.md       # Comprehensive deployment guide
├── test_auth.py              # Authentication system tests
├── scripts/
│   └── add_missing_columns.py # Database migration script
└── test_api.py               # Original API testing script
```

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd project1
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file with your credentials
   SECRET_KEY=your-secret-key-here
   MYSQL_USER=your_user
   MYSQL_PASSWORD=your_password
   MYSQL_HOST=your_host
   MYSQL_DB=your_database
   MYSQL_PORT=your_port
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   - **Full Application**: http://localhost:8000 (with authentication)
   - **Simple Form**: http://localhost:8000/simple (original form)
   - **API Documentation**: http://localhost:8000/docs

### 🌐 Production Deployment on Render

**Backend URL**: https://projscopebackend.onrender.com/

See [deployment_guide.md](deployment_guide.md) for complete deployment instructions.

## 📊 API Endpoints

### 🔐 Authentication
- `POST /auth/register` - User registration (students & faculty)
- `POST /auth/login` - User login with JWT token
- `GET /auth/me` - Get current user information

### 📝 Project Submissions (Students)
- `POST /submissions/` - Submit project for approval
- `GET /submissions/` - Get all submissions (faculty only)
- `PUT /submissions/{id}` - Review submission (faculty only)

### 🗂️ Projects (Faculty)
- `GET /projects/` - Get all approved projects (faculty only)
- `POST /projects/` - Add new project directly (faculty only)
- `PUT /projects/{id}` - Update project (faculty only)
- `DELETE /projects/{id}` - Delete project (faculty only)

### 🔍 Search (All authenticated users)
- `GET /projects/search?q=query` - Search projects by name, tools, or technologies

### 🏥 System
- `GET /` - Modern web interface with authentication
- `GET /simple` - Simple project submission form
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation

## 🎨 UI Features

### 🔐 Authentication Interface
- **Login/Register Tabs**: Seamless switching between forms
- **Role Selection**: Student or Faculty registration
- **Email Validation**: College email requirement (@mits.ac.in)
- **JWT Token Management**: Automatic token storage and refresh

### 👨‍🎓 Student Dashboard
- **Project Search**: Real-time search with instant results
- **Submission Form**: Comprehensive project idea submission
- **Project Discovery**: View existing projects and their details
- **Status Tracking**: See submission status and faculty feedback

### 👩‍🏫 Faculty Dashboard
- **Submission Review**: Approve/reject student submissions
- **Project Management**: Add, edit, and delete projects
- **Feedback System**: Add remarks and suggestions
- **Multi-tab Interface**: Organized workflow management

### 🎨 Design Features
- **Responsive Design**: Works on all devices
- **Modern UI**: Clean, professional interface
- **Color Scheme**: MITS college red/blue theme
- **Smooth Animations**: Enhanced user experience
- **Loading States**: Visual feedback for all actions
- **Error Handling**: User-friendly error messages

## 🗄️ Database Schema

### Users Table (Authentication)
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- 'student' or 'faculty'
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Project Submissions Table (Approval Workflow)
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
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'approved', 'rejected'
    student_id INT,
    approved_by INT,
    faculty_remarks TEXT,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed_at DATETIME,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);
```

### Projects Table (Approved Projects)
```sql
CREATE TABLE projects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_name VARCHAR(255) NOT NULL,
    idea VARCHAR(500) NOT NULL,
    team_members VARCHAR(255),
    roll_number VARCHAR(50),
    class_name VARCHAR(50),
    year INT,
    branch VARCHAR(100),
    sec VARCHAR(50),
    tools VARCHAR(255),
    technologies VARCHAR(255)
);
```

## 🧪 Testing

### Authentication System Tests
```bash
python test_auth.py
```

### Original API Tests
```bash
python test_api.py
```

### Manual Testing
1. **Registration**: Create student and faculty accounts
2. **Login**: Test authentication with both roles
3. **Student Flow**: Search projects, submit ideas
4. **Faculty Flow**: Review submissions, manage projects
5. **API Documentation**: Use `/docs` for interactive testing

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt encryption for passwords
- **Role-Based Access Control**: Different permissions for students and faculty
- **Email Validation**: College email domain restriction
- **CORS Configuration**: Secure cross-origin resource sharing
- **Input Validation**: Pydantic schemas for data validation

## 🚀 Deployment Status

- ✅ **Backend**: Deployed on Render with MySQL database
- ✅ **Frontend**: Modern authentication-enabled interface
- ✅ **Database**: Railway MySQL with all required tables
- ✅ **Authentication**: JWT-based user management
- ✅ **Role System**: Student and Faculty access levels
- ✅ **API Documentation**: Available at `/docs`

## 📱 Live Application

**🌐 Access the live application**: [https://projscopebackend.onrender.com](https://projscopebackend.onrender.com)

### Test Accounts
Create your own accounts using @mits.ac.in email addresses:
- **Students**: Can search projects and submit ideas
- **Faculty**: Can review submissions and manage projects

## 📞 Support & Documentation

- **Deployment Guide**: [deployment_guide.md](deployment_guide.md)
- **API Documentation**: Available at `/docs` endpoint
- **GitHub Repository**: Full source code and issues
- **Test Scripts**: Automated testing for all features

---

**🎓 Built for MITS College by Puneeth**  
**🚀 Deployed on Render with ❤️ using FastAPI, MySQL, and modern web technologies**