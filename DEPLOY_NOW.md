# 🚀 DEPLOY TO RENDER NOW

## Option 1: Simple Version (No Auth) - FASTEST

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy simple version"
   git push
   ```

2. **Render Setup**:
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect GitHub repo
   - **Build Command**: `pip install -r requirements_simple.txt`
   - **Start Command**: `python main_simple.py`

3. **Environment Variables**:
   ```
   MYSQL_USER=root
   MYSQL_PASSWORD=OxlvxnNzxEsnhhqBMAgurtxZnNSEctru
   MYSQL_HOST=maglev.proxy.rlwy.net
   MYSQL_DB=railway
   MYSQL_PORT=3306
   ```

4. **Deploy** → Done!

## Option 2: Full Authentication Version

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy auth version"
   git push
   ```

2. **Render Setup**:
   - **Build Command**: `pip install -r requirements_auth.txt`
   - **Start Command**: `python main_auth.py`

3. **Environment Variables**:
   ```
   SECRET_KEY=mits-college-secret-key-2024
   MYSQL_USER=root
   MYSQL_PASSWORD=OxlvxnNzxEsnhhqBMAgurtxZnNSEctru
   MYSQL_HOST=maglev.proxy.rlwy.net
   MYSQL_DB=railway
   MYSQL_PORT=3306
   ```

## 🎯 What You Get

### Simple Version:
- ✅ Project submission form
- ✅ CRUD operations
- ✅ Database integration
- ✅ Modern UI

### Auth Version:
- ✅ Student/Faculty login
- ✅ Role-based access
- ✅ Project approval workflow
- ✅ Search functionality
- ✅ Complete dashboard

## 🔗 URLs After Deployment

- **Frontend**: https://your-app-name.onrender.com
- **API Docs**: https://your-app-name.onrender.com/docs
- **Simple Form**: https://your-app-name.onrender.com/simple

## 🧪 Test Accounts (Auth Version)

Register with @mits.ac.in emails:
- **Student**: student@mits.ac.in
- **Faculty**: faculty@mits.ac.in

## ⚡ Quick Local Test

```bash
# Simple version
python main_simple.py

# Auth version  
python main_auth.py
```

Visit: http://localhost:8000

---

**🎉 Ready to deploy! Choose your version and follow the steps above.**