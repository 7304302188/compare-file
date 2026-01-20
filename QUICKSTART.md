# Quick Start Guide

## Prerequisites
- Python 3.8+ installed
- Node.js and npm installed

## Quick Setup

### 1. Backend Setup (Terminal 1)

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend will run on `http://localhost:8000`

### 2. Frontend Setup (Terminal 2)

```bash
cd frontend
npm install
npm start
```

Frontend will open at `http://localhost:3000`

## Testing

1. Prepare two ZIP files:
   - **ZIP 1**: Contains folders with PDFs named like `DAB7341_PLM-3001.pdf`
   - **ZIP 2**: Contains folders named like `DAB7341(47564) ANJUM SIRAJ` with PDFs inside

2. Open the React app in your browser
3. Upload both ZIP files
4. Click "Upload & Process"
5. The merged ZIP will automatically download

## Troubleshooting

- **CORS errors**: Make sure backend is running on port 8000
- **File upload fails**: Check that files are valid ZIP files
- **No PDFs found**: Verify the ZIP structure matches the expected format

