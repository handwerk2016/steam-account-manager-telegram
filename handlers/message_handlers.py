import logging
import json
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.decorators import restricted
from utils.message_formatter import format_account_message, get_main_keyboard
from utils.account_manager import process_data_line, save_processed_account
from utils.localization import get_text, get_user_language
from handlers.command_handlers import MAIN_MENU, ACCOUNT_LIST, WAITING_FOR_TEMPLATE
from handlers.account_handlers import show_account_list, download_all_accounts, confirm_clear_all
from handlers.language_handlers import show_language_menu
from handlers.asf_handlers import start_asf_config_generation

@restricted
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles text messages"""
    text = update.message.text.strip()
    lang = get_user_language(context)
    
    # Check if the text is a menu command
    if text == get_text("btn_account_list", lang):
        return await show_account_list(update, context)
    elif text == get_text("btn_refresh", lang):
        # Save current state in user_data
        context.user_data['state'] = MAIN_MENU
        await update.message.reply_text(
            get_text("data_updated", lang),
            reply_markup=get_main_keyboard(context)
        )
        return MAIN_MENU
    elif text == get_text("btn_download_all", lang):
        return await download_all_accounts(update, context)
    elif text == get_text("btn_clear_all", lang):
        return await confirm_clear_all(update, context)
    elif text == get_text("btn_help", lang):
        from handlers.command_handlers import help_command
        return await help_command(update, context)
    elif text == get_text("btn_import_zip", lang):
        # Save current state in user_data
        context.user_data['state'] = MAIN_MENU
        await update.message.reply_text(
            get_text("send_zip", lang),
            reply_markup=get_main_keyboard(context)
        )
        return MAIN_MENU
    elif text == get_text("btn_language", lang):
        return await show_language_menu(update, context)
    elif text == get_text("btn_asf_configs", lang):
        return await start_asf_config_generation(update, context)
    
    # If the text is not a command, try to process it as account data
    account_data = process_data_line(text)
    
    if account_data:
        # Save account data
        saved_data = save_processed_account(account_data)
        
        # Send message with account data
        await update.message.reply_text(
            format_account_message(saved_data, context),
            parse_mode='HTML',
            reply_markup=get_main_keyboard(context)
        )
    else:
        # If the text is not account data, send error message
        await update.message.reply_text(
            get_text("invalid_format", lang),
            reply_markup=get_main_keyboard(context)
        )
    
    return MAIN_MENU 