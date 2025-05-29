# A simple telegram bot to manage accounts

Well that's a small lil bro that helps you to manage your steam accounts. 


*I was testing this bro on Python 3.10, dunno if it will work on newer versions.*



It accepts files and messages in such format.

```bash
login:password:mail:mail_password:account_link

or

login:password:mail:mail_password
```

It also can work with `.zip` archives. The structure of an archive:

```bash
Archive.zip
├── accounts.txt
└── mafile/
    ├── mafile1.mafile
    ├── mafile2.mafile
    ├── ...
    └── mafileX.mafile
```

And also it can parse mafiles (from SDA or ArchiSteamFarm).

As we know maFile looks like this:

```bash
{
    "shared_secret":"XXXXXXXXXXXXXXX",
    "serial_number":"XXXXXXXXXXXXXXX",
    "revocation_code":"RXXXXX",
    "uri":"XXXXXXXXXXXXXXX",
    "server_time":XXXXXXXXXXXXXXX,
    "account_name":"XXXXXXXXXXXXXXX",
    "token_gid":"XXXXXXXXXXXXXXX",
    "identity_secret":"XXXXXXXXXXXXXXX",
    "secret_1":"XXXXXXXXXXXXXXX",
    "status":1,
    "device_id":"XXXXXXXXXX",
    "fully_enrolled":true,

    "Session":{
        "SteamID":"XXXXXXXXXXXXXXXXXXXX",
        "AccessToken":"XXXXXXXXXXXXXXXXXXXX",
        "RefreshToken":"XXXXXXXXXXXXXXXXXXXX",
        "SessionID":"XXXXXXXXXXXXXXXXXXXX",
        "SteamLoginSecure":"XXXXXXXXXXXXXXXXXXXX"
    }
}
```

So this bot can parse such files and read ``revocation_code`` to associate with an account based on ``SteamID``

All accounts data it stores in ``accounts.json`` it's not encrypted so be carefully.

It can also generate ASF (ArchiSteamFarm) configs for all your accounts. Just paste a template JSON as a text message or upload a .json file and it will create configs for each account with proper login/password and include maFiles if available. The template should look like this:

```bash
{
  "SteamLogin": "account1",
  "SteamPassword": "account1",
  "Enabled": true,
  "RemoteCommunication": 0
}
```

The bot will replace `SteamLogin` and `SteamPassword` with actual account data and pack everything into a nice ZIP archive ready to be used with ASF.

# Technical Details (for nerds who care)

Under the hood, this little bro works something like this:

1. **Conversation Handler System** - Bot uses FSM (Finite State Machine) via `ConversationHandler` to manage dialog flow:

```python
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        MAIN_MENU: [
            *common_handlers,
            CallbackQueryHandler(change_language, pattern="^lang_"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
        ],
        # Other states...
    },
    fallbacks=[CommandHandler("start", start)]
)
```

2. **Account Management Magic** - Identifies accounts by SteamID or login, extracts SteamIDs from profile URLs:

```python
def extract_steamid_from_url(url: str) -> str:
    """Extract SteamID from a Steam profile URL"""
    if not url:
        return ""

    # Look for SteamID in URL like https://steamcommunity.com/profiles/76561198921334935
    match = re.search(r'profiles/(\d+)', url)
    if match:
        return match.group(1)
    return ""
```

3. **ZIP Processing Wizardry** - Creates temp dirs, handles both UTF-8 and CP1251 encodings (cuz Cyrillic stuff, ya know):

```python
# Example of file decoding from ZIP archives
try:
    content = accounts_file.read().decode('utf-8')
except UnicodeDecodeError:
    content = accounts_file.read().decode('cp1251')
```

4. **Data Merging Sorcery** - Smart enough to combine data from different sources for the same account:

```python
def merge_account_data(existing_data, new_data):
    """Merge account data, keeping the best bits from both"""
    merged_data = existing_data.copy()

    # Update only fields that exist in new data and aren't empty
    for key, value in new_data.items():
        if value and value != "missing":
            merged_data[key] = value

    # Save that bad boi
    return merged_data
```

5. **ASF Config Generation** - Takes a template and spits out configs for all your accounts:

```python
# Create configs for each account
for account_id, account_data in accounts.items():
    # Skip accounts without login/password
    if not account_data.get('login') or account_data['login'] == "отсутствует":
        continue

    # Clone the template and replace login/password
    account_config = template.copy()
    account_config['SteamLogin'] = account_data['login']
    account_config['SteamPassword'] = account_data['password']

    # Add to ZIP archive
    config_name = f"{account_data['login']}.json"
    zip_file.writestr(config_name, json.dumps(account_config, indent=2))
```

6. **Bot Structure** - Simple but effective:
   
   - `handlers/` - Telegram command and message handlers
   - `utils/` - Helper functions and classes
   - `locales/` - i18n support (yeah, I actually bothered with that)

7. **maFile Parsing** - Extracts that sweet revocation code and SteamID:

```python
def process_mafile(content: str) -> dict:
    mafile_data = json.loads(content)

    # Get the goods
    account_name = mafile_data.get('account_name', "missing")
    r_code = mafile_data.get('revocation_code', "missing")
    steam_id = mafile_data.get('Session', {}).get('SteamID', "missing")

    # Format that profile URL like a boss
    link = f"https://steamcommunity.com/profiles/{steam_id}" if steam_id != "missing" else "missing"

    return {
        'login': account_name,
        'r_code': r_code,
        'steam_id': steam_id,
        'link': link,
        # etc...
    }
```

# How to use:

1. Clone the repo

2. Create virtual environment `python -m venv venv`

3. Activate **venv**. `source venv/bin/activate` (linux)

4. Install all requirements `pip install -r requirements.txt`

5. Configure bot in `config.py`

6. Start the bot `python main.py`

7. Type `/start` to bot and have fun.

# Why?

Cuz I'm reselling accounts from lolzteam. A lot of accounts so I need an account manager to manage them. And I need to make a *cool developer* portfolio or such.

Ngl I've used some Claude's help to understand and make some methods to works properly.
