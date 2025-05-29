import json
import os
import re
import logging

# Path to the accounts data file
ACCOUNTS_FILE = 'accounts.json'

def load_accounts():
    """Loading accounts data from file"""
    if not os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'w') as f:
            json.dump({}, f)
        return {}
    
    try:
        with open(ACCOUNTS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logging.error(f"Error reading file {ACCOUNTS_FILE}. Creating new file.")
        with open(ACCOUNTS_FILE, 'w') as f:
            json.dump({}, f)
        return {}

def save_accounts(accounts):
    """Saving accounts data to file"""
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts, f, indent=2)

def extract_steamid_from_url(url: str) -> str:
    """Extracting SteamID from Steam profile URL"""
    if not url:
        return ""
    
    # Looking for SteamID in URL like https://steamcommunity.com/profiles/76561198921334935
    match = re.search(r'profiles/(\d+)', url)
    if match:
        return match.group(1)
    return ""

def store_account_data(account_data):
    """Storing account data in file"""
    accounts = load_accounts()
    
    # If there is SteamID, use it as key
    if account_data.get('steam_id'):
        key = account_data['steam_id']
        accounts[key] = account_data
        logging.info(f"Account with SteamID {key} added to storage")
    # Otherwise use login as key
    elif account_data.get('login'):
        key = account_data['login']
        accounts[key] = account_data
        logging.info(f"Account with login {key} added to storage")
    
    # Save updated data
    save_accounts(accounts)

def find_matching_account(account_data):
    """Finding matching account in storage"""
    accounts = load_accounts()
    
    # If there is SteamID, search by it
    if account_data.get('steam_id') and account_data['steam_id'] in accounts:
        return accounts[account_data['steam_id']]
    
    # If there is login, search by it
    if account_data.get('login') and account_data['login'] in accounts:
        return accounts[account_data['login']]
    
    # If no matches, return None
    return None

def merge_account_data(existing_data, new_data):
    """Merging account data"""
    merged_data = existing_data.copy()
    
    # Update only those fields that exist in new data and are not empty
    for key, value in new_data.items():
        if value and value != "missing":
            merged_data[key] = value
    
    # Save updated data
    accounts = load_accounts()
    if merged_data.get('steam_id'):
        accounts[merged_data['steam_id']] = merged_data
    elif merged_data.get('login'):
        accounts[merged_data['login']] = merged_data
    save_accounts(accounts)
    
    return merged_data

def process_data_line(line: str) -> dict:
    """Processing one line of data"""
    parts = line.strip().split(':')
    if len(parts) < 4:
        return None
        
    login = parts[0]
    password = parts[1]
    mail = parts[2]
    mail_password = parts[3]
    
    # Check for link (everything after the 4th element)
    link = ':'.join(parts[4:]) if len(parts) > 4 else ""
    
    # Extract SteamID from link if present
    steam_id = extract_steamid_from_url(link)
    
    # Create dictionary with account data
    account_data = {
        'login': login,
        'password': password,
        'mail': mail,
        'mail_password': mail_password,
        'r_code': "missing",
        'steam_id': steam_id,
        'link': link,
        'mafile': {}
    }
    
    return account_data

def process_mafile(content: str) -> dict:
    """Processing maFile"""
    try:
        mafile_data = json.loads(content)
        
        # Get values
        account_name = mafile_data.get('account_name', "missing")
        r_code = mafile_data.get('revocation_code', "missing")
        steam_id = mafile_data.get('Session', {}).get('SteamID', "missing")
        
        # Create link if SteamID exists
        link = f"https://steamcommunity.com/profiles/{steam_id}" if steam_id != "missing" else "missing"
        
        # Create dictionary with account data from maFile
        account_data = {
            'login': account_name,
            'password': "missing",
            'mail': "missing",
            'mail_password': "missing",
            'r_code': r_code,
            'steam_id': steam_id,
            'link': link,
            'mafile': mafile_data
        }
        
        return account_data
        
    except json.JSONDecodeError:
        return None

def save_processed_account(account_data):
    """Saves processed account with check for matches"""
    # Check if there is a matching account in storage
    matching_account = find_matching_account(account_data)
    if matching_account:
        # If exists, merge data
        merged_data = merge_account_data(matching_account, account_data)
        logging.info(f"Account data {account_data.get('login')} merged with existing")
        return merged_data
    else:
        # If not, save new account
        store_account_data(account_data)
        return account_data

def delete_account(account_id):
    """Deleting account from storage"""
    accounts = load_accounts()
    if account_id in accounts:
        del accounts[account_id]
        save_accounts(accounts)
        return True
    return False

def clear_all_accounts():
    """Clearing all accounts"""
    save_accounts({})
    return True 