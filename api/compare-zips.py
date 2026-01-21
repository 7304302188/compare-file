from mangum import Mangum
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import zipfile
import os
import tempfile
import shutil
import re
import base64
from typing import Dict, Tuple

# Import all the processing functions from backend
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import (
    extract_username_from_pdf_name,
    extract_username_from_folder_name,
    extract_nested_zips,
    process_zip1,
    process_zip2,
    merge_pdfs
)

app = FastAPI(title="ZIP Comparison Tool")

# Enable CORS for React frontend - allow all origins for Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you might want to restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/compare-zips")
async def compare_zips(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...)
):
    """
    Upload and compare two ZIP files.
    Returns the merged result ZIP file.
    """
    # Validate file types
    if not file1.filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400, detail="File 1 must be a ZIP file")
    
    if not file2.filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400, detail="File 2 must be a ZIP file")
    
    # Create temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Save uploaded files
            zip1_path = os.path.join(temp_dir, "zip1.zip")
            zip2_path = os.path.join(temp_dir, "zip2.zip")
            
            with open(zip1_path, 'wb') as f:
                shutil.copyfileobj(file1.file, f)
            
            with open(zip2_path, 'wb') as f:
                shutil.copyfileobj(file2.file, f)
            
            # Validate ZIP files
            try:
                with zipfile.ZipFile(zip1_path, 'r') as z:
                    z.testzip()
            except zipfile.BadZipFile:
                raise HTTPException(status_code=400, detail="File 1 is not a valid ZIP file")
            
            try:
                with zipfile.ZipFile(zip2_path, 'r') as z:
                    z.testzip()
            except zipfile.BadZipFile:
                raise HTTPException(status_code=400, detail="File 2 is not a valid ZIP file")
            
            # Extract and process ZIP files
            zip1_extract_dir = os.path.join(temp_dir, "zip1_extract")
            zip2_extract_dir = os.path.join(temp_dir, "zip2_extract")
            os.makedirs(zip1_extract_dir, exist_ok=True)
            os.makedirs(zip2_extract_dir, exist_ok=True)
            
            zip1_pdfs, zip1_info = process_zip1(zip1_path, zip1_extract_dir)
            zip2_pdfs, zip2_info = process_zip2(zip2_path, zip2_extract_dir)
            
            if not zip1_pdfs and not zip2_pdfs:
                raise HTTPException(status_code=400, detail="No PDF files found in either ZIP file")
            
            # Merge PDFs and get summary
            result_zip_path, summary = merge_pdfs(zip1_pdfs, zip2_pdfs, zip1_info, zip2_info, temp_dir)
            
            # Read ZIP file and encode to base64
            with open(result_zip_path, 'rb') as f:
                zip_data = f.read()
                zip_base64 = base64.b64encode(zip_data).decode('utf-8')
            
            # Return JSON response with summary and ZIP file
            return JSONResponse({
                'success': True,
                'summary': summary,
                'zip_file': zip_base64,
                'filename': 'result.zip'
            })
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")


@app.get("/")
async def root():
    return {"message": "ZIP Comparison Tool API"}


# Create handler for Vercel serverless function
handler = Mangum(app)

