# 🚀 KAVA - Quick Start Guide

## How to Run the Project

### **Method 1: Automated Startup (Easiest!)**

Just double-click or run in terminal:

```bash
./start.sh
```

This will automatically:
- ✅ Start the backend on port 8000
- ✅ Start the frontend on port 3001
- ✅ Open both servers in background

Then open in browser: **http://localhost:3001**

### **Method 2: Manual Startup**

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open: **http://localhost:3001**

---

## 🛑 How to Stop the Project

### **Method 1: Automated Shutdown**

```bash
./stop.sh
```

### **Method 2: Manual Shutdown**

Press `Ctrl+C` in each terminal window

---

## 📋 Before First Run

Make sure you have:

1. **Python virtual environment setup:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Frontend dependencies installed:**
   ```bash
   cd frontend
   npm install
   ```

3. **Environment variables configured:**
   - Copy `.env.example` to `.env`
   - Add your `CLAUDE_API_KEY`

---

## ✨ Quick Access

- **Frontend:** http://localhost:3001
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 🎯 What the System Does

1. **Upload Documents** - Insurance policy, damage photos, receipts
2. **Create Claim Packet** - Organized claim with OCR processing
3. **AI Judge Validation** - Progressive 4-iteration analysis with bonuses
4. **Generate Outputs** - Final PDF report + ZIP package + Proof card

---

## 🆘 Troubleshooting

**Port already in use:**
```bash
./stop.sh  # Kill everything first
./start.sh # Then restart
```

**Backend not connecting:**
- Check if `CLAUDE_API_KEY` is set in `.env`
- Make sure virtual environment is activated

**Frontend not loading:**
- Run `npm install` in frontend directory
- Check if port 3001 is free

---

Enjoy using KAVA! 🎉
