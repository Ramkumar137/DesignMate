# Sketch2Design Setup Guide

## Environment Variables

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000
```

### Backend (backend/.env)
```bash
GEMINI_API_KEY=your_actual_gemini_api_key_here
CORS_ORIGINS=http://localhost:8080,http://localhost:3000,http://localhost:5173
```

## Running the Application

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
npm install
npm run dev
```

## API Endpoints

- **Generate Image**: `POST /generate/run`
- **AI Assistant**: `POST /ai-assistant/chat`
- **Health Check**: `GET /health`

## Features

✅ Upload sketch images
✅ Generate AI designs using ControlNet
✅ AI Assistant powered by Gemini API
✅ Real-time chat interface
✅ Loading states and error handling
✅ Responsive UI with Tailwind CSS

