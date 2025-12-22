# 🚀 Railway Deployment Fix Guide

## ❌ **Problem**
Railway deployment crashed dengan error "image push" karena **tidak ada Dockerfile**.

## ✅ **Solution**

### **Files Created:**
1. `Dockerfile` - Docker configuration untuk Railway
2. `.dockerignore` - Exclude unnecessary files

---

## 📋 **Deployment Steps**

### **Step 1: Commit & Push**

```bash
git add Dockerfile .dockerignore
git commit -m "Add Dockerfile for Railway deployment"
git push origin main
```

### **Step 2: Configure Railway Environment Variables**

Di Railway Dashboard, tambahkan environment variables:

**Required:**
```
DATABASE_URL_DIRECT=postgresql://postgres:YOUR_PASSWORD@db.ujwqvweresyqvdmjidlr.supabase.co:5432/postgres
DATABASE_URL_SESSION=postgresql://postgres.ujwqvweresyqvdmjidlr:YOUR_PASSWORD@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres
JWT_SECRET=your-super-secret-jwt-key-min-32-characters
```

**Optional:**
```
PORT=8000
```

### **Step 3: Trigger Redeploy**

Railway akan auto-deploy setelah push, atau manual trigger:
1. Buka Railway Dashboard
2. Pilih service "ml-stroke-guard"
3. Klik "Deploy" → "Redeploy"

---

## 🔍 **Verify Deployment**

Setelah deploy sukses, test endpoints:

```bash
# Health check
curl https://ml-stroke-guard-production-745c.up.railway.app/health

# Root endpoint
curl https://ml-stroke-guard-production-745c.up.railway.app/
```

---

## ⚠️ **Important Notes**

### **1. Environment Variables**
Pastikan semua env vars sudah di-set di Railway Dashboard:
- `DATABASE_URL_SESSION` (recommended untuk Railway)
- `JWT_SECRET`

### **2. Port Configuration**
Railway auto-assign PORT, tapi kita expose 8000 di Dockerfile.

### **3. Health Check**
Dockerfile include health check ke `/health` endpoint.

---

## 🐛 **Troubleshooting**

### **If build fails:**
1. Check build logs di Railway
2. Verify `requirements.txt` complete
3. Check Python version compatibility

### **If runtime fails:**
1. Check runtime logs
2. Verify environment variables
3. Check database connection

### **If health check fails:**
1. Verify `/health` endpoint exists
2. Check if app is listening on correct port

---

## 📝 **Next Steps After Successful Deploy**

1. ✅ Test all endpoints
2. ✅ Update frontend API_BASE_URL to Railway URL
3. ✅ Test end-to-end flow
4. ✅ Monitor logs for errors

---

**Railway URL:** https://ml-stroke-guard-production-745c.up.railway.app

---

## 🎯 **Quick Commands**

```bash
# Commit Dockerfile
git add Dockerfile .dockerignore
git commit -m "Add Dockerfile for Railway"
git push

# Watch Railway logs
# (via Railway Dashboard → Deployments → View Logs)

# Test deployed API
curl https://ml-stroke-guard-production-745c.up.railway.app/
```

---

**Status:** ✅ Ready to deploy!
