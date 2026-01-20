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

app = FastAPI(title="ZIP Comparison Tool")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def extract_username_from_pdf_name(pdf_name: str) -> str:
    """
    Extract USERNAME from PDF filename.
    Format: USERNAME_CODE.pdf
    Example: DAB7341_PLM-3001.pdf -> DAB7341
    """
    # Remove .pdf extension
    name_without_ext = pdf_name.replace('.pdf', '').replace('.PDF', '')
    # Split by underscore and take first part (USERNAME)
    parts = name_without_ext.split('_')
    if parts:
        return parts[0]
    return None


def extract_username_from_folder_name(folder_name: str) -> str:
    """
    Extract USERNAME from folder name.
    Format: USERNAME(NUMBER) NAME
    Example: DAB7341(47564) ANJUM SIRAJ -> DAB7341
    Also handles: DAD5823(47425) MD RAJAUR RAHMAN -> DAD5823
    """
    # Match pattern: USERNAME(NUMBER) or just USERNAME
    # This pattern matches alphanumeric characters before an opening parenthesis
    match = re.match(r'^([A-Z0-9]+)\(', folder_name)
    if match:
        return match.group(1)
    # If no parentheses, try to extract first word (alphanumeric)
    parts = folder_name.split()
    if parts:
        # Remove any trailing characters that aren't part of username
        username = re.match(r'^([A-Z0-9]+)', parts[0])
        if username:
            return username.group(1)
    return None


def extract_nested_zips(root_dir: str, max_depth: int = 5, current_depth: int = 0):
    """
    Recursively extract nested ZIP files found in the directory.
    Prevents infinite recursion with max_depth parameter.
    Returns the number of nested ZIPs extracted.
    """
    if current_depth >= max_depth:
        return 0
    
    extracted_count = 0
    
    # Find and extract nested ZIP files
    # Use list() to avoid modifying dirs while iterating
    for root, dirs, files in list(os.walk(root_dir)):
        for file in files:
            if file.lower().endswith('.zip'):
                nested_zip_path = os.path.join(root, file)
                try:
                    # Create extraction directory for nested ZIP (use a cleaner name)
                    zip_name_without_ext = os.path.splitext(file)[0]
                    nested_extract_dir = os.path.join(root, zip_name_without_ext)
                    os.makedirs(nested_extract_dir, exist_ok=True)
                    
                    print(f"Extracting nested ZIP: {file} -> {nested_extract_dir}")
                    
                    # Extract nested ZIP
                    with zipfile.ZipFile(nested_zip_path, 'r') as nested_zip:
                        nested_zip.extractall(nested_extract_dir)
                    
                    # Remove the original nested ZIP file to avoid confusion
                    os.remove(nested_zip_path)
                    extracted_count += 1
                    
                    # Recursively extract any ZIPs inside the nested ZIP
                    extracted_count += extract_nested_zips(nested_extract_dir, max_depth, current_depth + 1)
                    
                except (zipfile.BadZipFile, Exception) as e:
                    print(f"Warning: Could not extract nested ZIP {nested_zip_path}: {str(e)}")
                    continue
    
    return extracted_count


def process_zip1(zip_path: str, extract_dir: str) -> Tuple[Dict[str, str], Dict[str, Dict]]:
    """
    Process ZIP File 1: Extract PDFs and map USERNAME -> PDF path.
    ZIP contains 1-2 folders, each with multiple PDFs named USERNAME_CODE.pdf
    Also extracts nested ZIP files recursively.
    Returns: (username_to_pdf dict, file_info dict with folder and filename details)
    """
    username_to_pdf = {}
    file_info = {}  # username -> {folder, filename, full_path}
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    # Extract any nested ZIP files
    nested_count = extract_nested_zips(extract_dir)
    if nested_count > 0:
        print(f"Extracted {nested_count} nested ZIP file(s) from ZIP 1")
    
    # Walk through extracted directory (including nested ZIP contents)
    for root, dirs, files in os.walk(extract_dir):
        # Get relative folder path from extract_dir
        rel_path = os.path.relpath(root, extract_dir)
        folder_name = rel_path if rel_path != '.' else 'root'
        
        for file in files:
            # Skip ZIP files (they should have been extracted already)
            if file.lower().endswith('.zip'):
                continue
                
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                username = extract_username_from_pdf_name(file)
                if username:
                    # Store the PDF path for this username
                    username_to_pdf[username] = pdf_path
                    # Store file info for summary (folder name includes nested ZIP structure)
                    file_info[username] = {
                        'folder': folder_name,
                        'filename': file,
                        'source': 'ZIP File 1'
                    }
                else:
                    print(f"Warning: Could not extract username from {file}")
    
    return username_to_pdf, file_info


def rename_zip_to_pdf(root_dir: str):
    """
    Rename any .zip files to .pdf in the directory tree.
    This is used for ZIP 2 where files may be misnamed as .zip but are actually PDFs.
    """
    renamed_count = 0
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.zip'):
                zip_path = os.path.join(root, file)
                # Create new filename with .pdf extension
                pdf_filename = os.path.splitext(file)[0] + '.pdf'
                pdf_path = os.path.join(root, pdf_filename)
                
                # Check if a file with the target name already exists
                if os.path.exists(pdf_path):
                    # If target exists, use a unique name
                    base_name = os.path.splitext(file)[0]
                    counter = 1
                    while os.path.exists(pdf_path):
                        pdf_filename = f"{base_name}_{counter}.pdf"
                        pdf_path = os.path.join(root, pdf_filename)
                        counter += 1
                
                try:
                    os.rename(zip_path, pdf_path)
                    print(f"Renamed {file} to {pdf_filename} in {root}")
                    renamed_count += 1
                except Exception as e:
                    print(f"Warning: Could not rename {zip_path} to {pdf_path}: {str(e)}")
                    continue
    
    return renamed_count


def process_zip2(zip_path: str, extract_dir: str) -> Tuple[Dict[str, str], Dict[str, Dict]]:
    """
    Process ZIP File 2: Extract PDFs and map USERNAME -> PDF path.
    ZIP contains multiple folders named USERNAME(NUMBER) NAME, each with one PDF.
    Also extracts nested ZIP files recursively.
    After extracting nested ZIPs, any remaining .zip files are renamed to .pdf.
    Returns: (username_to_pdf dict, file_info dict with folder and filename details)
    """
    username_to_pdf = {}
    file_info = {}  # username -> {folder, filename, full_path}
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    # Extract any nested ZIP files
    nested_count = extract_nested_zips(extract_dir)
    if nested_count > 0:
        print(f"Extracted {nested_count} nested ZIP file(s) from ZIP 2")
    
    # Rename any remaining .zip files to .pdf (they might be misnamed PDFs)
    renamed_count = rename_zip_to_pdf(extract_dir)
    if renamed_count > 0:
        print(f"Renamed {renamed_count} .zip file(s) to .pdf in ZIP 2")
    
    # Walk through extracted directory (including nested ZIP contents)
    for root, dirs, files in os.walk(extract_dir):
        # Get relative folder path from extract_dir
        rel_path = os.path.relpath(root, extract_dir)
        # For ZIP 2, we use the folder name for username extraction
        folder_name = os.path.basename(root) if rel_path != '.' else 'root'
        full_folder_path = rel_path if rel_path != '.' else 'root'
        
        # Try to extract username from folder name first
        username = extract_username_from_folder_name(folder_name)
        
        # Look for PDF in this folder
        for file in files:
            # Skip ZIP files (they should have been extracted already)
            if file.lower().endswith('.zip'):
                continue
                
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                # If we don't have a username from folder, try to get it from PDF name
                if not username:
                    username = extract_username_from_pdf_name(file)
                
                if username:
                    # If username already exists, we might have a duplicate - keep the first one found
                    # But for ZIP 2, we want to track all files, so we'll use a unique key
                    # Store the PDF path (will be overwritten if duplicate, but that's OK for now)
                    username_to_pdf[username] = pdf_path
                    # Store file info for summary (use full path to show nested structure)
                    file_info[username] = {
                        'folder': full_folder_path,
                        'filename': file,
                        'source': 'ZIP File 2'
                    }
                    print(f"Processed PDF: {file} in folder '{full_folder_path}' (username: {username})")
                else:
                    print(f"Warning: Could not extract username from folder {folder_name} or file {file} (full path: {full_folder_path})")
                    # Still track the file even if we can't extract username
                    # Use a placeholder username based on the file name
                    placeholder_username = os.path.splitext(file)[0][:20]  # Use first 20 chars of filename
                    if placeholder_username not in username_to_pdf:
                        username_to_pdf[placeholder_username] = pdf_path
                        file_info[placeholder_username] = {
                            'folder': full_folder_path,
                            'filename': file,
                            'source': 'ZIP File 2'
                        }
                        print(f"Processed PDF with placeholder username: {file} in folder '{full_folder_path}' (placeholder: {placeholder_username})")
    
    return username_to_pdf, file_info


def merge_pdfs(zip1_pdfs: Dict[str, str], zip2_pdfs: Dict[str, str], 
               zip1_info: Dict[str, Dict], zip2_info: Dict[str, Dict], 
               output_dir: str) -> Tuple[str, Dict]:
    """
    Merge PDFs from both ZIPs, avoiding duplicates by username.
    If same username exists in both, keep only one (prefer zip1, then zip2).
    Returns: (path to result ZIP file, summary dict with removed files info)
    """
    # Create output directory for final PDFs
    pdfs_dir = os.path.join(output_dir, "merged_pdfs")
    os.makedirs(pdfs_dir, exist_ok=True)
    
    # Collect all unique usernames
    all_usernames = set(zip1_pdfs.keys()) | set(zip2_pdfs.keys())
    
    # Track which files were kept and removed
    kept_files = []
    removed_files = []
    
    # Copy PDFs, preferring zip1 over zip2 for duplicates
    for username in all_usernames:
        pdf_path = None
        source_info = None
        removed_info = None
        
        # Prefer zip1, fallback to zip2
        if username in zip1_pdfs:
            pdf_path = zip1_pdfs[username]
            source_info = zip1_info.get(username, {})
            # If also in zip2, mark zip2 as removed
            if username in zip2_pdfs:
                removed_info = zip2_info.get(username, {})
        elif username in zip2_pdfs:
            pdf_path = zip2_pdfs[username]
            source_info = zip2_info.get(username, {})
        
        if pdf_path:
            # Get original filename
            original_filename = os.path.basename(pdf_path)
            # Create new filename: USERNAME.pdf (clean format)
            new_filename = f"{username}.pdf"
            dest_path = os.path.join(pdfs_dir, new_filename)
            
            # Copy PDF to output directory
            shutil.copy2(pdf_path, dest_path)
            
            # Track kept file
            kept_files.append({
                'username': username,
                'source': source_info.get('source', 'Unknown'),
                'folder': source_info.get('folder', 'Unknown'),
                'filename': source_info.get('filename', original_filename)
            })
            
            # Track removed file if duplicate
            if removed_info:
                removed_files.append({
                    'username': username,
                    'source': removed_info.get('source', 'Unknown'),
                    'folder': removed_info.get('folder', 'Unknown'),
                    'filename': removed_info.get('filename', 'Unknown'),
                    'reason': f'Duplicate - kept from {source_info.get("source", "Unknown")} instead'
                })
    
    # Create ZIP file from merged PDFs
    result_zip_path = os.path.join(output_dir, "result.zip")
    with zipfile.ZipFile(result_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pdf_file in os.listdir(pdfs_dir):
            pdf_path = os.path.join(pdfs_dir, pdf_file)
            if os.path.isfile(pdf_path):
                zipf.write(pdf_path, pdf_file)
    
    # Build comprehensive file lists from both ZIPs
    zip1_all_files = []
    zip2_all_files = []
    
    for username, info in zip1_info.items():
        is_duplicate = username in zip2_pdfs
        status = 'duplicate' if is_duplicate else 'unique'
        # zip1 files are always kept (we prefer zip1 over zip2)
        zip1_all_files.append({
            'username': username,
            'folder': info.get('folder', 'Unknown'),
            'filename': info.get('filename', 'Unknown'),
            'status': status,
            'kept': True  # All zip1 files are kept
        })
    
    for username, info in zip2_info.items():
        is_duplicate = username in zip1_pdfs
        status = 'duplicate' if is_duplicate else 'unique'
        # zip2 files are kept only if not duplicate (if duplicate, zip1 is kept instead)
        zip2_all_files.append({
            'username': username,
            'folder': info.get('folder', 'Unknown'),
            'filename': info.get('filename', 'Unknown'),
            'status': status,
            'kept': not is_duplicate  # zip2 kept only if not duplicate
        })
    
    # Build duplicate pairs information
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
                'kept_from': 'ZIP File 1',  # Always prefer zip1
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

