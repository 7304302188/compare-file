# Backend - ZIP Comparison Tool

Python FastAPI backend for comparing and merging ZIP files.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `POST /api/compare-zips` - Upload two ZIP files and get merged result
  - Parameters: `file1` (ZIP), `file2` (ZIP)
  - Returns: Merged ZIP file download

