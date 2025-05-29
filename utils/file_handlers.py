import os
import zipfile
import io
import json
import tempfile
from utils.account_manager import load_accounts

def create_account_zip(account_data):
    """Creates ZIP archive with data of one account"""
    # Create buffer for archive
    zip_buffer = io.BytesIO()
    
    # Create ZIP archive in memory
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Create filename based on login
        account_name = account_data['login']
        
        # Create content of text file
        # Add line with data in format login:password:mail:mailpassword
        account_info = f"{account_data['login']}:{account_data['password']}:{account_data['mail']}:{account_data['mail_password']}\n\n"
        
        # Add additional information in readable format
        account_info += f"Login: {account_data['login']}\n"
        account_info += f"Password: {account_data['password']}\n"
        account_info += f"Email: {account_data['mail']}\n"
        account_info += f"Email password: {account_data['mail_password']}\n"
        account_info += f"R-code: {account_data['r_code']}\n"
        account_info += f"SteamID: {account_data['steam_id']}\n"
        account_info += f"Link: {account_data['link']}\n"
        
        # Add text file to archive
        zip_file.writestr(f"{account_name}.txt", account_info)
        
        # If there is maFile, add it to archive
        if account_data.get('mafile') and account_data['mafile']:
            # Save in single-line format for compatibility
            mafile_content = json.dumps(account_data['mafile'], separators=(',', ':'))
            zip_file.writestr(f"{account_name}.maFile", mafile_content)
    
    # Return buffer with archive
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def create_all_accounts_zip():
    """Creates ZIP archive with all accounts"""
    # Load all accounts
    accounts = load_accounts()
    
    # If there are no accounts, return None
    if not accounts:
        return None
    
    # Create buffer for archive
    zip_buffer = io.BytesIO()
    
    # Create ZIP archive in memory
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Create temporary directory for maFile
        mafile_dir = "mafile"
        
        # Create content of accounts.txt file
        accounts_txt = ""
        
        # Add each account to archive
        for account_id, account_data in accounts.items():
            # Add line with data in format login:password:mail:mailpassword:link
            accounts_txt += f"{account_data['login']}:{account_data['password']}:{account_data['mail']}:{account_data['mail_password']}:{account_data['link']}\n"
            
            # If there is maFile, add it to archive
            if account_data.get('mafile') and account_data['mafile']:
                # Save in single-line format for compatibility
                mafile_content = json.dumps(account_data['mafile'], separators=(',', ':'))
                mafile_name = f"{account_data['login']}.maFile"
                zip_file.writestr(f"{mafile_dir}/{mafile_name}", mafile_content)
        
        # Add accounts.txt file to archive
        zip_file.writestr("accounts.txt", accounts_txt)
    
    # Return buffer with archive
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def create_asf_configs_zip(template_json):
    """Creates ZIP archive with ASF configs for all accounts"""
    # Load all accounts
    accounts = load_accounts()
    
    # If there are no accounts, return None
    if not accounts:
        return None
    
    try:
        # Load ASF config template
        template = json.loads(template_json)
    except json.JSONDecodeError:
        return None
    
    # Create buffer for archive
    zip_buffer = io.BytesIO()
    
    # Create ZIP archive in memory
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add each account to archive
        for account_id, account_data in accounts.items():
            # Skip accounts without login or password
            if not account_data.get('login') or account_data['login'] == "missing" or not account_data.get('password') or account_data['password'] == "missing":
                continue
            
            # Create copy of template for this account
            account_config = template.copy()
            
            # Replace login and password in template
            account_config['SteamLogin'] = account_data['login']
            account_config['SteamPassword'] = account_data['password']
            
            # Convert config to JSON and add to archive
            config_content = json.dumps(account_config, indent=2)
            config_name = f"{account_data['login']}.json"
            zip_file.writestr(config_name, config_content)
            
            # If there is maFile, add it to archive
            if account_data.get('mafile') and account_data['mafile']:
                # Save in single-line format for compatibility
                mafile_content = json.dumps(account_data['mafile'], separators=(',', ':'))
                mafile_name = f"{account_data['login']}.maFile"
                zip_file.writestr(mafile_name, mafile_content)
    
    # Return buffer with archive
    zip_buffer.seek(0)
    return zip_buffer.getvalue() 