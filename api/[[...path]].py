from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import zipfile
import os
import tempfile
import shutil
import re
import base64
from typing import Dict, Tuple

app = FastAPI(title="ZIP Comparison Tool")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)


# Explicit OPTIONS handler for compare-zips
@app.options("/api/compare-zips")
async def options_compare_zips():
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


def extract_username_from_pdf_name(pdf_name: str) -> str:
    """
    Extract USERNAME from PDF filename.
    Format: USERNAME_CODE.pdf
    Example: DAB7341_PLM-3001.pdf -> DAB7341
    """
    name_without_ext = pdf_name.replace('.pdf', '').replace('.PDF', '')
    parts = name_without_ext.split('_')
    if parts:
        return parts[0]
    return None


def extract_username_from_folder_name(folder_name: str) -> str:
    """
    Extract USERNAME from folder name.
    Format: USERNAME(NUMBER) NAME
    Example: DAB7341(47564) ANJUM SIRAJ -> DAB7341
    """
    match = re.match(r'^([A-Z0-9]+)\(', folder_name)
    if match:
        return match.group(1)
    parts = folder_name.split()
    if parts:
        username = re.match(r'^([A-Z0-9]+)', parts[0])
        if username:
            return username.group(1)
    return None


def extract_nested_zips(root_dir: str, max_depth: int = 5, current_depth: int = 0):
    """
    Recursively extract nested ZIP files found in the directory.
    """
    if current_depth >= max_depth:
        return 0
    
    extracted_count = 0
    
    for root, dirs, files in list(os.walk(root_dir)):
        for file in files:
            if file.lower().endswith('.zip'):
                nested_zip_path = os.path.join(root, file)
                try:
                    zip_name_without_ext = os.path.splitext(file)[0]
                    nested_extract_dir = os.path.join(root, zip_name_without_ext)
                    os.makedirs(nested_extract_dir, exist_ok=True)
                    
                    with zipfile.ZipFile(nested_zip_path, 'r') as nested_zip:
                        nested_zip.extractall(nested_extract_dir)
                    
                    os.remove(nested_zip_path)
                    extracted_count += 1
                    extracted_count += extract_nested_zips(nested_extract_dir, max_depth, current_depth + 1)
                    
                except (zipfile.BadZipFile, Exception):
                    continue
    
    return extracted_count


def process_zip1(zip_path: str, extract_dir: str) -> Tuple[Dict[str, str], Dict[str, Dict]]:
    """
    Process ZIP File 1: Extract PDFs and map USERNAME -> PDF path.
    """
    username_to_pdf = {}
    file_info = {}
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    extract_nested_zips(extract_dir)
    
    for root, dirs, files in os.walk(extract_dir):
        rel_path = os.path.relpath(root, extract_dir)
        folder_name = rel_path if rel_path != '.' else 'root'
        
        for file in files:
            if file.lower().endswith('.zip'):
                continue
                
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                username = extract_username_from_pdf_name(file)
                if username:
                    username_to_pdf[username] = pdf_path
                    file_info[username] = {
                        'folder': folder_name,
                        'filename': file,
                        'source': 'ZIP File 1'
                    }
    
    return username_to_pdf, file_info


def rename_zip_to_pdf(root_dir: str):
    """
    Rename any .zip files to .pdf in the directory tree.
    """
    renamed_count = 0
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.zip'):
                zip_path = os.path.join(root, file)
                pdf_filename = os.path.splitext(file)[0] + '.pdf'
                pdf_path = os.path.join(root, pdf_filename)
                
                if os.path.exists(pdf_path):
                    base_name = os.path.splitext(file)[0]
                    counter = 1
                    while os.path.exists(pdf_path):
                        pdf_filename = f"{base_name}_{counter}.pdf"
                        pdf_path = os.path.join(root, pdf_filename)
                        counter += 1
                
                try:
                    os.rename(zip_path, pdf_path)
                    renamed_count += 1
                except Exception:
                    continue
    
    return renamed_count


def process_zip2(zip_path: str, extract_dir: str) -> Tuple[Dict[str, str], Dict[str, Dict]]:
    """
    Process ZIP File 2: Extract PDFs and map USERNAME -> PDF path.
    """
    username_to_pdf = {}
    file_info = {}
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    extract_nested_zips(extract_dir)
    rename_zip_to_pdf(extract_dir)
    
    for root, dirs, files in os.walk(extract_dir):
        rel_path = os.path.relpath(root, extract_dir)
        folder_name = os.path.basename(root) if rel_path != '.' else 'root'
        full_folder_path = rel_path if rel_path != '.' else 'root'
        
        username = extract_username_from_folder_name(folder_name)
        
        for file in files:
            if file.lower().endswith('.zip'):
                continue
                
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                if not username:
                    username = extract_username_from_pdf_name(file)
                
                if username:
                    username_to_pdf[username] = pdf_path
                    file_info[username] = {
                        'folder': full_folder_path,
                        'filename': file,
                        'source': 'ZIP File 2'
                    }
                else:
                    placeholder_username = os.path.splitext(file)[0][:20]
                    if placeholder_username not in username_to_pdf:
                        username_to_pdf[placeholder_username] = pdf_path
                        file_info[placeholder_username] = {
                            'folder': full_folder_path,
                            'filename': file,
                            'source': 'ZIP File 2'
                        }
    
    return username_to_pdf, file_info


def merge_pdfs(zip1_pdfs: Dict[str, str], zip2_pdfs: Dict[str, str], 
               zip1_info: Dict[str, Dict], zip2_info: Dict[str, Dict], 
               output_dir: str) -> Tuple[str, Dict]:
    """
    Merge PDFs from both ZIPs, avoiding duplicates by username.
    """
    pdfs_dir = os.path.join(output_dir, "merged_pdfs")
    os.makedirs(pdfs_dir, exist_ok=True)
    
    all_usernames = set(zip1_pdfs.keys()) | set(zip2_pdfs.keys())
    
    kept_files = []
    removed_files = []
    
    for username in all_usernames:
        pdf_path = None
        source_info = None
        removed_info = None
        
        if username in zip1_pdfs:
            pdf_path = zip1_pdfs[username]
            source_info = zip1_info.get(username, {})
            if username in zip2_pdfs:
                removed_info = zip2_info.get(username, {})
        elif username in zip2_pdfs:
            pdf_path = zip2_pdfs[username]
            source_info = zip2_info.get(username, {})
        
        if pdf_path:
            original_filename = os.path.basename(pdf_path)
            new_filename = f"{username}.pdf"
            dest_path = os.path.join(pdfs_dir, new_filename)
            
            shutil.copy2(pdf_path, dest_path)
            
            kept_files.append({
                'username': username,
                'source': source_info.get('source', 'Unknown'),
                'folder': source_info.get('folder', 'Unknown'),
                'filename': source_info.get('filename', original_filename)
            })
            
            if removed_info:
                removed_files.append({
                    'username': username,
                    'source': removed_info.get('source', 'Unknown'),
                    'folder': removed_info.get('folder', 'Unknown'),
                    'filename': removed_info.get('filename', 'Unknown'),
                    'reason': f'Duplicate - kept from {source_info.get("source", "Unknown")} instead'
                })
    
    result_zip_path = os.path.join(output_dir, "result.zip")
    with zipfile.ZipFile(result_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pdf_file in os.listdir(pdfs_dir):
            pdf_path = os.path.join(pdfs_dir, pdf_file)
            if os.path.isfile(pdf_path):
                zipf.write(pdf_path, pdf_file)
    
    zip1_all_files = []
    zip2_all_files = []
    
    for username, info in zip1_info.items():
        is_duplicate = username in zip2_pdfs
        status = 'duplicate' if is_duplicate else 'unique'
        zip1_all_files.append({
            'username': username,
            'folder': info.get('folder', 'Unknown'),
            'filename': info.get('filename', 'Unknown'),
            'status': status,
            'kept': True
        })
    
    for username, info in zip2_info.items():
        is_duplicate = username in zip1_pdfs
        status = 'duplicate' if is_duplicate else 'unique'
        zip2_all_files.append({
            'username': username,
            'folder': info.get('folder', 'Unknown'),
            'filename': info.get('filename', 'Unknown'),
            'status': status,
            'kept': not is_duplicate
        })
    
    duplicate_pairs = []
    for username in all_usernames:
        if username in zip1_pdfs and username in zip2_pdfs:
            zip1_info_item = zip1_info.get(username, {})
            zip2_info_item = zip2_info.get(username, {})
            duplicate_pairs.append({
                'username': username,
                'zip1_file': {
                    'folder': zip1_info_item.get('folder', 'Unknown'),
                    'filename': zip1_info_item.get('filename', 'Unknown')
                },
                'zip2_file': {
                    'folder': zip2_info_item.get('folder', 'Unknown'),
                    'filename': zip2_info_item.get('filename', 'Unknown')
                },
                'kept_from': 'ZIP File 1',
                'removed_from': 'ZIP File 2'
            })
    
    summary = {
        'zip1_stats': {
            'total_files': len(zip1_all_files),
            'unique_files': len([f for f in zip1_all_files if f['status'] == 'unique']),
            'duplicate_files': len([f for f in zip1_all_files if f['status'] == 'duplicate']),
            'files': zip1_all_files
        },
        'zip2_stats': {
            'total_files': len(zip2_all_files),
            'unique_files': len([f for f in zip2_all_files if f['status'] == 'unique']),
            'duplicate_files': len([f for f in zip2_all_files if f['status'] == 'duplicate']),
            'files': zip2_all_files
        },
        'duplicate_pairs': duplicate_pairs,
        'final_merged': {
            'total_files': len(kept_files),
            'files': kept_files
        },
        'summary_stats': {
            'total_kept': len(kept_files),
            'total_removed': len(removed_files),
            'total_duplicates': len(duplicate_pairs)
        }
    }
    
    return result_zip_path, summary


@app.post("/api/compare-zips")
async def compare_zips(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...)
):
    """
    Upload and compare two ZIP files.
    Returns the merged result ZIP file.
    """
    if not file1.filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400, detail="File 1 must be a ZIP file")
    
    if not file2.filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400, detail="File 2 must be a ZIP file")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            zip1_path = os.path.join(temp_dir, "zip1.zip")
            zip2_path = os.path.join(temp_dir, "zip2.zip")
            
            with open(zip1_path, 'wb') as f:
                shutil.copyfileobj(file1.file, f)
            
            with open(zip2_path, 'wb') as f:
                shutil.copyfileobj(file2.file, f)
            
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
            
            zip1_extract_dir = os.path.join(temp_dir, "zip1_extract")
            zip2_extract_dir = os.path.join(temp_dir, "zip2_extract")
            os.makedirs(zip1_extract_dir, exist_ok=True)
            os.makedirs(zip2_extract_dir, exist_ok=True)
            
            zip1_pdfs, zip1_info = process_zip1(zip1_path, zip1_extract_dir)
            zip2_pdfs, zip2_info = process_zip2(zip2_path, zip2_extract_dir)
            
            if not zip1_pdfs and not zip2_pdfs:
                raise HTTPException(status_code=400, detail="No PDF files found in either ZIP file")
            
            result_zip_path, summary = merge_pdfs(zip1_pdfs, zip2_pdfs, zip1_info, zip2_info, temp_dir)
            
            with open(result_zip_path, 'rb') as f:
                zip_data = f.read()
                zip_base64 = base64.b64encode(zip_data).decode('utf-8')
            
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


@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "ZIP Comparison API is running"}

@app.post("/api/test")
async def test_post():
    return {"status": "ok", "message": "POST works"}

@app.get("/api")
async def api_root():
    return {"status": "ok", "message": "ZIP Comparison API"}

