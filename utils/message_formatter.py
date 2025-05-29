from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from utils.localization import get_text, get_user_language

def get_main_keyboard(context):
    """Updates keyboard for main menu considering user language"""
    lang = get_user_language(context)
    
    keyboard = [
        [get_text("btn_account_list", lang), get_text("btn_refresh", lang)],
        [get_text("btn_import_zip", lang), get_text("btn_download_all", lang)],
        [get_text("btn_asf_configs", lang), get_text("btn_clear_all", lang)],
        [get_text("btn_language", lang), get_text("btn_help", lang)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def format_message_line(label: str, value: str, code_block: bool = True) -> str:
    """Formatting one line of message using HTML tags"""
    if not value:
        value = "missing"
    
    if code_block:
        # Use pre for monospaced text that can be copied
        return f"{label}: <pre>{value}</pre>"
    else:
        # For links use regular text
        return f"{label}: {value}"

def format_account_message(account_data, context):
    """Formatting message with account data considering user language"""
    lang = get_user_language(context)
    
    # Use template from localization
    template = get_text("account_format", lang)
    
    # Process steam_id to show "missing" if it's not present
    steam_id = account_data['steam_id'] if account_data['steam_id'] else "missing"
    
    # Process link to show "missing" if it's not present
    link = account_data['link'] or "missing"
    
    # Format message with account data
    return template.format(
        login=account_data['login'],
        password=account_data['password'],
        mail=account_data['mail'],
        mail_password=account_data['mail_password'],
        r_code=account_data['r_code'],
        steam_id=steam_id,
        link=link
    )

def get_account_list_markup(accounts, page=0, items_per_page=10, context=None):
    """Creating keyboard with account list considering user language"""
    lang = get_user_language(context) if context else 'ru'
    keyboard = []
    
    # Get list of account keys
    account_keys = list(accounts.keys())
    
    # Calculate start and end indices for current page
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(account_keys))
    
    # Add buttons for each account on current page
    for i in range(start_idx, end_idx):
        key = account_keys[i]
        account = accounts[key]
        # Use login or SteamID as button text
        button_text = account.get('login', key)
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"account_{key}")])
    
    # Add navigation buttons
    navigation = []
    if page > 0:
        navigation.append(InlineKeyboardButton(get_text("btn_prev_page", lang), callback_data=f"page_{page-1}"))
    if end_idx < len(account_keys):
        navigation.append(InlineKeyboardButton(get_text("btn_next_page", lang), callback_data=f"page_{page+1}"))
    
    if navigation:
        keyboard.append(navigation)
    
    # Add button to return to main menu
    keyboard.append([InlineKeyboardButton(get_text("btn_back_to_main", lang), callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(keyboard)

def get_account_detail_markup(account_id, context=None):
    """Creating keyboard for account details considering user language"""
    lang = get_user_language(context) if context else 'ru'
    keyboard = [
        [InlineKeyboardButton(get_text("btn_download_account", lang), callback_data=f"download_{account_id}")],
        [InlineKeyboardButton(get_text("btn_delete_account", lang), callback_data=f"delete_{account_id}")],
        [InlineKeyboardButton(get_text("btn_back_to_list", lang), callback_data="back_to_list")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_delete_markup(context=None):
    """Creating keyboard for confirmation of deleting all accounts considering user language"""
    lang = get_user_language(context) if context else 'ru'
    keyboard = [
        [InlineKeyboardButton(get_text("btn_confirm_clear", lang), callback_data="confirm_clear_all")],
        [InlineKeyboardButton(get_text("btn_cancel_clear", lang), callback_data="cancel_clear_all")]
    ]
    return InlineKeyboardMarkup(keyboard) 