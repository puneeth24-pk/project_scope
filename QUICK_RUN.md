# 🚀 QUICK RUN GUIDE

## ⚡ Local Testing (No Database Required)

```bash
python main_local.py
```
Visit: http://localhost:8000

## 🌐 Deploy to Render

### 1. Push to GitHub
```bash
git add .
git commit -m "Deploy project scope"
git push
```

### 2. Render Setup
- Go to https://dashboard.render.com
- New Web Service → Connect GitHub
- **Build Command**: `pip install -r requirements_simple.txt`
- **Start Command**: `python main_fixed.py`

### 3. Environment Variables
```
MYSQL_USER=root
MYSQL_PASSWORD=OxlvxnNzxEsnhhqBMAgurtxZnNSEctru
MYSQL_HOST=maglev.proxy.rlwy.net
MYSQL_DB=railway
MYSQL_PORT=27275
```

## ✅ What Works

### Local Version:
- ✅ Runs without database
- ✅ In-memory storage
- ✅ Full web interface
- ✅ Project submission & viewing

### Deployed Version:
- ✅ Connects to Railway database
- ✅ Persistent storage
- ✅ Full CRUD operations
- ✅ Modern web interface

## 🎯 URLs After Deploy

- **Main App**: https://your-app.onrender.com
- **API Docs**: https://your-app.onrender.com/docs
- **Health Check**: https://your-app.onrender.com/health

---

**🎉 Ready to run locally or deploy to Render!**