import json
import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import DEFAULT_LANGUAGE

# Available languages
AVAILABLE_LANGUAGES = {
    'ru': '🇷🇺 Русский',
    'en': '🇬🇧 English'
}

# Path to locales directory
LOCALES_DIR = 'locales'

# Cache for locales
_locales_cache = {}

def load_locale(lang_code):
    """Loads localization for specified language"""
    if lang_code in _locales_cache:
        return _locales_cache[lang_code]
    
    try:
        file_path = os.path.join(LOCALES_DIR, f"{lang_code}.json")
        with open(file_path, 'r', encoding='utf-8') as f:
            locale_data = json.load(f)
            _locales_cache[lang_code] = locale_data
            return locale_data
    except Exception as e:
        logging.error(f"Error loading locale {lang_code}: {e}")
        # If failed to load localization, return Russian (default)
        if lang_code != 'ru':
            return load_locale('ru')
        return {}

def get_text(key, lang_code, *args, **kwargs):
    """Gets text by key for specified language"""
    locale_data = load_locale(lang_code)
    
    # Get text by key
    text = locale_data.get(key, key)
    
    # Format text using parameters
    if args or kwargs:
        try:
            if kwargs:
                # Try to use named parameters
                text = text.format(**kwargs)
            else:
                # If that fails, try to use positional parameters
                text = text.format(*args)
        except:
            # If that fails too, return unformatted text
            pass
    
    return text

def get_language_keyboard():
    """Creates keyboard for language selection"""
    keyboard = []
    
    # Add button for each language
    for lang_code, lang_name in AVAILABLE_LANGUAGES.items():
        keyboard.append([InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}")])
    
    return InlineKeyboardMarkup(keyboard)

def is_supported_language(lang_code):
    """Checks if specified language is supported"""
    return lang_code in AVAILABLE_LANGUAGES

def get_user_language(context):
    """Gets user language from context"""
    if context.user_data and 'language' in context.user_data:
        return context.user_data['language']
    
    # Check that default language is supported
    if is_supported_language(DEFAULT_LANGUAGE):
        return DEFAULT_LANGUAGE
    
    # If default language is not supported, return Russian
    return 'ru'

def set_user_language(context, lang_code):
    """Sets user language in context"""
    if is_supported_language(lang_code):
        context.user_data['language'] = lang_code
        return True
    return False

def get_available_languages():
    """Returns dictionary of available languages"""
    return AVAILABLE_LANGUAGES 