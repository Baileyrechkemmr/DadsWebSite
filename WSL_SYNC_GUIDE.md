# 🔄 WSL Workspace Sync Guide

## 📥 **Pulling Changes to WSL**

### 1. **Basic Git Pull**
```bash
cd /path/to/omimi_swords
git pull origin main
```

### 2. **Check What Changed**
```bash
git log --oneline -5  # See recent commits
git diff HEAD~1 --name-only  # See files that changed
```

---

## 🔧 **WSL Workspace Setup Commands**

### For **Fresh/Partial Workspaces** - Run These:

```bash
# 1. Navigate to project
cd /path/to/omimi_swords

# 2. Pull latest changes
git pull origin main

# 3. Set up Python virtual environment (if not exists)
python3 -m venv venv
source venv/bin/activate

# 4. Install/update dependencies  
pip install -r requirements.txt

# 5. Copy environment variables (IMPORTANT!)
# You need to recreate .env file since it's gitignored
cp .env.example .env  # If you have example file
# OR manually create .env with:
cat > .env << 'EOF'
DEBUG=True
SECRET_KEY=django-insecure-91!8xc543hj37*md&s1*wgfr+p)l+ow=n7bgu4ci5pi#)sz*qc

AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME=ominisword-images
AWS_S3_REGION=us-east-1
USE_S3=True

EMAIL_HOST_USER=brechkemmer01@gmail.com
EMAIL_HOST_PASSWORD=bqtlyuyacnxwbjyj
EOF

# 6. Run database migrations
python manage.py migrate

# 7. Test the setup
python manage.py check
```

---

## 🚀 **For Already-Setup Workspaces**

If your WSL workspace was already working, you just need:

```bash
# Quick sync for existing workspaces
cd /path/to/omimi_swords
git pull origin main
source venv/bin/activate
pip install -r requirements.txt  # In case new packages added
python manage.py migrate        # Apply any new migrations
```

---

## ⚠️ **Key Differences in Our Changes**

### **What Changed:**
1. **`omimi/settings.py`**: Fixed S3 signed URLs (`AWS_QUERYSTRING_AUTH = True`)
2. **`omimi/urls.py`**: Removed local media conflicts
3. **New packages**: Added `requests` to requirements.txt
4. **New files**: Documentation and testing scripts

### **WSL-Specific Notes:**
- ✅ **All changes are Linux-compatible** (WSL is Linux)
- ✅ **S3 integration works identically** on WSL
- ✅ **No platform-specific adjustments needed**

---

## 🧪 **Test Your WSL Setup**

```bash
# Activate environment
source venv/bin/activate

# Test the fixes work
python manage.py runserver

# In another terminal, test image loading:
curl -s http://127.0.0.1:8000/sales/ | grep -c "X-Amz-Algorithm"
# Should return a number > 0 (signed URLs present)
```

---

## 🔄 **Sync Script (Optional)**

Create this as `sync_wsl.sh` for easy future syncing:

```bash
#!/bin/bash
echo "🔄 Syncing WSL workspace..."

git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py check

echo "✅ WSL workspace synced and ready!"
```

---

## 📋 **TL;DR - Quick Commands**

### **For Working WSL Workspace:**
```bash
git pull origin main
source venv/bin/activate  
pip install -r requirements.txt
python manage.py migrate
```

### **For Fresh/Broken WSL Workspace:**
```bash
git pull origin main
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Create .env file (copy from above)
python manage.py migrate
```

**The key thing**: Make sure your `.env` file exists in WSL since it's not in git! 🔑