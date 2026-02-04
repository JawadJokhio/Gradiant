# Pakistan Geography Tutor App

An interactive web application designed to help students learn Pakistan's geography using Vision AI and GIS data.

## Project Structure
- `frontend/`: React + Vite + Leaflet
- `backend/`: FastAPI + Python
- `data/`: GIS datasets for Pakistan

## How to Run

### 1. Start the Backend
```powershell
cd backend
# Recommended: Create and activate a venv
# python -m venv venv
# .\venv\Scripts\Activate.ps1
pip install fastapi uvicorn python-multipart
python main.py
```

### 2. Start the Frontend
```powershell
cd frontend
npm install
npm run dev
```

## Features
- **Map Upload**: Upload any map image of Pakistan.
- **Natural Language Queries**: Ask questions like "Where are the rice-growing regions?" or "Show me the Indus river."
- **Interactive Visualization**: Results are overlaid on a GIS-powered map with educational markers and regions.
- **Academic Info**: Provides curriculum-aligned facts for students preparing for examinations.
