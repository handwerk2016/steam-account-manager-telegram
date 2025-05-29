import os
import json
import zipfile
import tempfile
import logging
from io import BytesIO

def process_zip_archive(zip_bytes):
    """
    Processes ZIP archive, extracts account data and maFiles.
    
    Args:
        zip_bytes: byte content of ZIP archive
        
    Returns:
        tuple: (list of lines from accounts.txt, list of maFile contents, list of errors)
    """
    processed_accounts = []
    processed_mafiles = []
    errors = []
    
    try:
        # Create temporary directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            # Open ZIP archive
            with zipfile.ZipFile(BytesIO(zip_bytes), 'r') as zip_ref:
                # Get list of files in archive
                file_list = zip_ref.namelist()
                
                # Look for accounts.txt
                accounts_txt_path = None
                for file_path in file_list:
                    if file_path.lower().endswith('accounts.txt'):
                        accounts_txt_path = file_path
                        break
                
                # Process accounts.txt if found
                if accounts_txt_path:
                    try:
                        with zip_ref.open(accounts_txt_path) as accounts_file:
                            try:
                                content = accounts_file.read().decode('utf-8')
                            except UnicodeDecodeError:
                                content = accounts_file.read().decode('cp1251')
                            
                            # Process each line
                            for line in content.split('\n'):
                                if line.strip():
                                    processed_accounts.append(line.strip())
                    except Exception as e:
                        errors.append(f"Error processing accounts.txt: {str(e)}")
                else:
                    errors.append("File accounts.txt not found in archive")
                
                # Look for mafile directory or .mafile files in root
                mafile_dir = None
                mafiles = []
                
                # First check for mafile/ directory
                for file_path in file_list:
                    if file_path.lower().startswith('mafile/') and file_path.lower().endswith('.mafile'):
                        mafiles.append(file_path)
                
                # If directory not found, look for .mafile in root
                if not mafiles:
                    for file_path in file_list:
                        if file_path.lower().endswith('.mafile') and '/' not in file_path:
                            mafiles.append(file_path)
                
                # Process found mafiles
                for mafile_path in mafiles:
                    try:
                        with zip_ref.open(mafile_path) as mafile:
                            try:
                                content = mafile.read().decode('utf-8')
                            except UnicodeDecodeError:
                                content = mafile.read().decode('cp1251')
                            
                            # Check that it's valid JSON
                            try:
                                json_content = json.loads(content)
                                processed_mafiles.append(content)
                            except json.JSONDecodeError:
                                errors.append(f"File {mafile_path} is not valid JSON")
                    except Exception as e:
                        errors.append(f"Error processing {mafile_path}: {str(e)}")
                
                if not mafiles:
                    errors.append(".mafile files not found in archive")
    
    except zipfile.BadZipFile:
        errors.append("Invalid ZIP archive")
    except Exception as e:
        errors.append(f"Error processing archive: {str(e)}")
    
    return processed_accounts, processed_mafiles, errors 