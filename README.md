# ZIP Comparison Tool

A full-stack application for comparing and merging ZIP files containing PDFs organized by username.

## Project Structure

```
compare-file/
├── backend/          # Python FastAPI backend
│   ├── main.py      # Main API server
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/
│   ├── public/
│   └── package.json
└── README.md
```

## Features

- Upload two ZIP files for comparison
- Extract usernames from PDF filenames (ZIP 1) and folder names (ZIP 2)
- Merge PDFs avoiding duplicates by username
- Download merged result as a ZIP file
- Clean, modern UI with error handling

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The app will open at `http://localhost:5173` (Vite default port)

## Usage

1. Start both backend and frontend servers
2. Open the React app in your browser
3. Select ZIP File 1 (contains folders with PDFs named `USERNAME_CODE.pdf`)
4. Select ZIP File 2 (contains folders named `USERNAME(NUMBER) NAME` with PDFs)
5. Click "Upload & Process"
6. The merged ZIP file will automatically download

## ZIP File Formats

### ZIP File 1
- Contains 1-2 folders
- Each folder contains multiple PDF files
- PDF naming: `USERNAME_CODE.pdf` (e.g., `DAB7341_PLM-3001.pdf`)

### ZIP File 2
- Contains multiple folders
- Folder naming: `USERNAME(NUMBER) NAME` (e.g., `DAB7341(47564) ANJUM SIRAJ`)
- Each folder contains exactly one PDF file

## How It Works

1. **Upload**: Both ZIP files are uploaded to the backend
2. **Extraction**: ZIPs are extracted to temporary directories
3. **Username Extraction**:
   - From ZIP 1: Extracted from PDF filenames (part before underscore)
   - From ZIP 2: Extracted from folder names (part before parentheses)
4. **Merging**: PDFs are merged by username, avoiding duplicates
5. **Result**: A new ZIP file is created with all unique PDFs in a flat structure
6. **Download**: The result ZIP is automatically downloaded

## API Endpoints

- `POST /api/compare-zips` - Upload two ZIP files and receive merged result
  - Parameters: `file1` (ZIP), `file2` (ZIP)
  - Returns: ZIP file download

## Technologies

- **Backend**: Python, FastAPI, Uvicorn
- **Frontend**: React, CSS3
- **File Processing**: Python zipfile, shutil

