import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.decorators import restricted
from utils.message_formatter import get_main_keyboard
from utils.localization import get_text, get_user_language, get_available_languages
from config import DEFAULT_LANGUAGE

# States for ConversationHandler
MAIN_MENU, ACCOUNT_LIST, ACCOUNT_DETAIL, ACCOUNT_EDIT, ACCOUNT_DELETE, CONFIRM_DELETE_ALL, WAITING_FOR_TEMPLATE = range(7)

@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /start command"""
    lang = get_user_language(context)
    
    # Save current state in user_data
    context.user_data['state'] = MAIN_MENU
    
    await update.message.reply_text(
        get_text("welcome", lang),
        reply_markup=get_main_keyboard(context)
    )
    return MAIN_MENU

@restricted
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /help command"""
    lang = get_user_language(context)
    
    # Save current state in user_data
    context.user_data['state'] = MAIN_MENU
    
    help_text = get_text("help_text", lang)
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard(context)
    )
    return MAIN_MENU

@restricted
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler for returning to main menu"""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_language(context)
    
    # Save current state in user_data
    context.user_data['state'] = MAIN_MENU
    
    # Send new message with keyboard
    await query.message.reply_text(
        get_text("main_menu", lang),
        reply_markup=get_main_keyboard(context)
    )
    
    # Delete or edit old message
    await query.edit_message_text(get_text("back_to_main", lang))
    
    return MAIN_MENU

@restricted
async def config_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /config command"""
    lang = get_user_language(context)
    
    # Save current state in user_data
    context.user_data['state'] = MAIN_MENU
    
    # Get dictionary of available languages
    available_languages = get_available_languages()
    
    # Create message with configuration information
    config_text = f"*{get_text('config_title', lang)}*\n\n"
    
    # Default language
    default_lang_name = available_languages.get(DEFAULT_LANGUAGE, 'Unknown')
    config_text += f"*{get_text('default_language', lang, DEFAULT_LANGUAGE, default_lang_name)}*\n"
    
    # Current language
    current_lang_name = available_languages.get(lang, 'Unknown')
    config_text += f"*{get_text('current_language', lang, lang, current_lang_name)}*\n\n"
    
    # Available languages
    config_text += f"*{get_text('available_languages', lang)}*\n"
    
    for code, name in available_languages.items():
        config_text += f"{get_text('language_item', lang, code, name)}\n"
    
    await update.message.reply_text(
        config_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard(context)
    )
    return MAIN_MENU 