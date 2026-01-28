# Deployment Guide - Resume Analyzer

This guide shows you how to deploy the application to test it from a URL.

## Quick Deploy Options

### Option 1: Render.com (Recommended - Free & Easy)

Render provides free hosting for both backend and frontend.

#### Step 1: Push to GitHub
```bash
# Make sure all files are committed
git add .
git commit -m "Add deployment configuration"
git push origin main
```

#### Step 2: Deploy Backend on Render

1. Go to [https://render.com](https://render.com) and sign up/login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `resume-analyzer-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Select **"Free"**
5. Click **"Create Web Service"**
6. Wait for deployment (3-5 minutes)
7. **Copy the URL** (e.g., `https://resume-analyzer-backend.onrender.com`)

#### Step 3: Deploy Frontend on Render

1. Click **"New +"** → **"Static Site"**
2. Select your repository
3. Configure:
   - **Name**: `resume-analyzer-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
4. Add Environment Variable:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: `https://resume-analyzer-backend.onrender.com` (your backend URL from Step 2)
5. Click **"Create Static Site"**
6. Wait for deployment (2-3 minutes)
7. **Your app is live!** Access at the provided URL

---

### Option 2: Railway.app (Alternative - Easy)

Railway offers generous free tier and simple deployment.

#### Deploy Backend

1. Go to [https://railway.app](https://railway.app) and login with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Railway will auto-detect settings
5. Add these variables:
   - `PORT`: 8000
   - `PYTHON_VERSION`: 3.11.0
6. Deploy and copy the URL

#### Deploy Frontend

1. Create new project in Railway
2. Select your repository
3. Set root directory to `frontend`
4. Add environment variable:
   - `VITE_API_BASE_URL`: (your backend URL)
5. Deploy

---

### Option 3: Vercel (Frontend) + Render (Backend)

#### Backend on Render
Follow "Option 1 - Step 2" above

#### Frontend on Vercel

1. Go to [https://vercel.com](https://vercel.com)
2. Click **"Import Project"**
3. Import from GitHub
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add Environment Variable:
   - **VITE_API_BASE_URL**: (your Render backend URL)
6. Deploy

---

### Option 4: Heroku (Classic)

#### Prerequisites
```bash
# Install Heroku CLI
# Windows: Download from https://devcenter.heroku.com/articles/heroku-cli
# Mac: brew install heroku/brew/heroku
```

#### Deploy Backend
```bash
cd backend
heroku create resume-analyzer-backend
git subtree push --prefix backend heroku main

# Or use Heroku dashboard
```

---

## Local Testing Before Deployment

Test the production build locally:

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend

# Create .env file with backend URL
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Build and preview
npm run build
npm run preview
```

Visit http://localhost:4173 to test

---

## Environment Variables

### Backend
No special environment variables needed. CORS is already configured for all origins.

### Frontend
- `VITE_API_BASE_URL`: Your deployed backend URL

---

## Troubleshooting

### Backend won't start
- Check logs in your hosting platform
- Verify `requirements.txt` is in backend folder
- Ensure Python 3.9+ is being used

### Frontend can't connect to backend
- Check CORS settings in `backend/app/main.py`
- Verify `VITE_API_BASE_URL` is set correctly
- Check browser console for errors

### 502/503 Errors
- Free tier services "sleep" after inactivity
- First request may take 30-60 seconds to wake up
- This is normal on free tiers

---

## Free Tier Limitations

### Render.com
- ✅ 750 hours/month free
- ⚠️ Services sleep after 15 minutes of inactivity
- ⚠️ 500MB RAM limit
- ✅ Unlimited static sites

### Railway.app
- ✅ $5 free credit per month
- ✅ No sleep on inactivity
- ⚠️ Usage-based billing after free credit

### Vercel
- ✅ Unlimited static deployments
- ✅ 100GB bandwidth/month
- ✅ No sleep on inactivity

---

## Testing Your Deployment

Once deployed, test these features:

1. ✅ Visit frontend URL
2. ✅ Click "Load Sample Data"
3. ✅ Click "Analyze"
4. ✅ Verify results appear
5. ✅ Test PDF upload
6. ✅ Test export (JSON/Markdown/PDF)
7. ✅ Test Admin Panel

---

## Quick Start Summary

**Fastest Path to Test URL:**

1. Push code to GitHub
2. Sign up for Render.com
3. Deploy backend (5 minutes)
4. Deploy frontend with backend URL (3 minutes)
5. **Done!** Test at your Render URL

Total time: ~10 minutes

---

## Need Help?

- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs

---

**Your app is ready to deploy! Choose the option that works best for you.** 🚀
