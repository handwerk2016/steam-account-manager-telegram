import logging
from telegram import Update, InputFile
from telegram.ext import ContextTypes, ConversationHandler
from utils.decorators import restricted
from utils.message_formatter import (
    get_account_list_markup, 
    get_account_detail_markup, 
    format_account_message,
    get_confirm_delete_markup,
    get_main_keyboard
)
from utils.account_manager import load_accounts, delete_account, clear_all_accounts
from utils.file_handlers import create_account_zip, create_all_accounts_zip
from utils.localization import get_text, get_user_language
from handlers.command_handlers import MAIN_MENU, ACCOUNT_LIST, ACCOUNT_DETAIL, ACCOUNT_EDIT, ACCOUNT_DELETE, CONFIRM_DELETE_ALL

@restricted
async def show_account_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows the list of accounts"""
    accounts = load_accounts()
    lang = get_user_language(context)
    
    # Save current state in user_data
    context.user_data['state'] = ACCOUNT_LIST
    
    if not accounts:
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            await query.edit_message_text(get_text("account_list_empty", lang))
        else:
            await update.message.reply_text(
                get_text("account_list_empty", lang),
                reply_markup=get_main_keyboard(context)
            )
        return MAIN_MENU
    
    # Get page number from context or set to 0 if not specified
    page = 0
    if update.callback_query:
        # If this is a callback_query, extract page number from callback_data
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("page_"):
            page = int(query.data.split("_")[1])
            context.user_data['page'] = page
        
        await query.edit_message_text(
            get_text("account_list_title", lang, len(accounts)),
            reply_markup=get_account_list_markup(accounts, page, context=context)
        )
    else:
        # If this is a regular message, send a new message
        await update.message.reply_text(
            get_text("account_list_title", lang, len(accounts)),
            reply_markup=get_account_list_markup(accounts, page, context=context)
        )
    
    return ACCOUNT_LIST

@restricted
async def show_account_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows details of the selected account"""
    query = update.callback_query
    await query.answer()
    lang = get_user_language(context)
    
    # Save current state in user_data
    context.user_data['state'] = ACCOUNT_DETAIL
    
    # Extract account ID from callback_data
    account_id = query.data.split("_")[1]
    
    # Load account data
    accounts = load_accounts()
    if account_id not in accounts:
        await query.edit_message_text(
            get_text("account_not_found", lang),
            reply_markup=get_account_list_markup(accounts, context=context)
        )
        return ACCOUNT_LIST
    
    account_data = accounts[account_id]
    
    # Save account ID in context for use in other handlers
    context.user_data['current_account'] = account_id
    
    # Send message with account details
    await query.edit_message_text(
        format_account_message(account_data, context),
        reply_markup=get_account_detail_markup(account_id, context),
        parse_mode='HTML'
    )
    
    return ACCOUNT_DETAIL

@restricted
async def delete_account_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Deletes the selected account"""
    query = update.callback_query
    await query.answer()
    lang = get_user_language(context)
    
    # Extract account ID from callback_data
    account_id = query.data.split("_")[1]
    
    # Delete account
    if delete_account(account_id):
        await query.edit_message_text(get_text("account_deleted", lang))
    else:
        await query.edit_message_text(get_text("account_delete_error", lang))
    
    # Return to account list
    return await show_account_list(update, context)

@restricted
async def confirm_clear_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Requests confirmation to delete all accounts"""
    lang = get_user_language(context)
    
    # Save current state in user_data
    context.user_data['state'] = CONFIRM_DELETE_ALL
    
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            get_text("confirm_clear_all", lang),
            reply_markup=get_confirm_delete_markup(context)
        )
    else:
        await update.message.reply_text(
            get_text("confirm_clear_all", lang),
            reply_markup=get_confirm_delete_markup(context)
        )
    
    return CONFIRM_DELETE_ALL

@restricted
async def clear_all_accounts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Deletes all accounts"""
    query = update.callback_query
    await query.answer()
    lang = get_user_language(context)
    
    # Delete all accounts
    if clear_all_accounts():
        await query.edit_message_text(get_text("all_accounts_cleared", lang))
    else:
        await query.edit_message_text(get_text("clear_all_error", lang))
    
    # Send new message with keyboard
    await query.message.reply_text(
        get_text("choose_action", lang),
        reply_markup=get_main_keyboard(context)
    )
    
    return MAIN_MENU

@restricted
async def cancel_clear_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels deletion of all accounts"""
    query = update.callback_query
    await query.answer()
    lang = get_user_language(context)
    
    await query.edit_message_text(get_text("clear_all_cancelled", lang))
    
    # Send new message with keyboard
    await query.message.reply_text(
        get_text("choose_action", lang),
        reply_markup=get_main_keyboard(context)
    )
    
    return MAIN_MENU

@restricted
async def back_to_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns to account list"""
    query = update.callback_query
    await query.answer()
    lang = get_user_language(context)
    
    # Edit current message
    await query.edit_message_text(get_text("back_to_list", lang))
    
    # Return to account list
    return await show_account_list(update, context)

@restricted
async def download_all_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sends ZIP archive with all accounts"""
    # Create ZIP archive
    zip_data = create_all_accounts_zip()
    lang = get_user_language(context)
    
    if not zip_data:
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            await query.edit_message_text(get_text("account_list_empty", lang))
        else:
            await update.message.reply_text(
                get_text("account_list_empty", lang),
                reply_markup=get_main_keyboard(context)
            )
        return MAIN_MENU
    
    # Send ZIP archive
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        # Send ZIP archive
        await query.message.reply_document(
            document=InputFile(zip_data, filename="accounts.zip"),
            caption=get_text("all_accounts", lang),
            reply_markup=get_main_keyboard(context)
        )
        
        # Edit original message
        await query.edit_message_text(get_text("download_all_accounts", lang))
    else:
        # Send ZIP archive
        await update.message.reply_document(
            document=InputFile(zip_data, filename="accounts.zip"),
            caption=get_text("all_accounts", lang),
            reply_markup=get_main_keyboard(context)
        )
    
    return MAIN_MENU

@restricted
async def download_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sends ZIP archive with selected account"""
    query = update.callback_query
    await query.answer()
    lang = get_user_language(context)
    
    # Extract account ID from callback_data
    account_id = query.data.split("_")[1]
    
    # Load account data
    accounts = load_accounts()
    if account_id not in accounts:
        await query.edit_message_text(
            get_text("account_not_found", lang),
            reply_markup=get_account_list_markup(accounts, context=context)
        )
        return ACCOUNT_LIST
    
    account_data = accounts[account_id]
    
    # Create ZIP archive
    zip_data = create_account_zip(account_data)
    
    # Send ZIP archive
    await query.message.reply_document(
        document=InputFile(zip_data, filename=f"{account_data['login']}.zip"),
        caption=get_text("account_caption", lang, account_data['login']),
        reply_markup=get_main_keyboard(context)
    )
    
    # Edit original message
    await query.edit_message_text(
        format_account_message(account_data, context),
        reply_markup=get_account_detail_markup(account_id, context),
        parse_mode='HTML'
    )
    
    return ACCOUNT_DETAIL 