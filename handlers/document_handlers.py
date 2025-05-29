import logging
import json
from telegram import Update, InputFile
from telegram.ext import ContextTypes, ConversationHandler
from utils.decorators import restricted
from utils.message_formatter import format_account_message, get_main_keyboard
from utils.account_manager import process_mafile, save_processed_account, process_data_line
from utils.localization import get_text, get_user_language
from utils.zip_processor import process_zip_archive
from utils.file_handlers import create_asf_configs_zip
from handlers.command_handlers import MAIN_MENU, WAITING_FOR_TEMPLATE

@restricted
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles documents (files)"""
    document = update.message.document
    file_name = document.file_name.lower() if document.file_name else ""
    lang = get_user_language(context)
    
    # Check if the user is in the ASF template waiting state
    user_data = context.user_data
    current_state = user_data.get('state')
    
    # Get the file
    file = await context.bot.get_file(document.file_id)
    file_bytes = await file.download_as_bytearray()
    
    # If user is in the ASF template waiting state and uploads a .json file,
    # process it as an ASF config template
    if current_state == WAITING_FOR_TEMPLATE and file_name.endswith('.json'):
        # Reset the state in user_data
        context.user_data['state'] = MAIN_MENU
        
        try:
            # Check that the file is valid JSON
            template_content = file_bytes.decode('utf-8')
            json.loads(template_content)
            
            # Create ZIP archive with configs
            zip_data = create_asf_configs_zip(template_content)
            
            if zip_data:
                # Send archive to the user
                await update.message.reply_document(
                    document=InputFile(zip_data, filename="asf_configs.zip"),
                    caption=get_text("asf_configs_generated", lang),
                    reply_markup=get_main_keyboard(context)
                )
            else:
                await update.message.reply_text(
                    get_text("asf_configs_error", lang),
                    reply_markup=get_main_keyboard(context)
                )
        except UnicodeDecodeError:
            await update.message.reply_text(
                get_text("encoding_error", lang),
                reply_markup=get_main_keyboard(context)
            )
        except json.JSONDecodeError:
            await update.message.reply_text(
                get_text("invalid_json", lang),
                reply_markup=get_main_keyboard(context)
            )
        except Exception as e:
            logging.error(f"Error processing ASF template: {e}")
            await update.message.reply_text(
                get_text("asf_configs_error", lang),
                reply_markup=get_main_keyboard(context)
            )
        
        return MAIN_MENU
    
    # Check file type for normal processing
    if file_name.endswith('.mafile'):
        # Process maFile
        try:
            content = file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                content = file_bytes.decode('cp1251')
            except UnicodeDecodeError:
                await update.message.reply_text(
                    get_text("encoding_error", lang),
                    reply_markup=get_main_keyboard(context)
                )
                return MAIN_MENU
        
        # Process maFile
        account_data = process_mafile(content)
        
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
            await update.message.reply_text(
                get_text("mafile_error", lang),
                reply_markup=get_main_keyboard(context)
            )
    
    elif file_name.endswith('.zip'):
        # Process ZIP archive
        processed_accounts, processed_mafiles, errors = process_zip_archive(file_bytes)
        
        # Counters for statistics
        accounts_count = 0
        mafiles_count = 0
        
        # Process accounts from accounts.txt
        for line in processed_accounts:
            account_data = process_data_line(line)
            if account_data:
                save_processed_account(account_data)
                accounts_count += 1
        
        # Process maFiles
        for mafile_content in processed_mafiles:
            account_data = process_mafile(mafile_content)
            if account_data:
                save_processed_account(account_data)
                mafiles_count += 1
        
        # Create results message
        result_message = get_text("zip_processed", lang) + "\n\n"
        result_message += get_text("accounts_processed", lang, accounts_count) + "\n"
        result_message += get_text("mafiles_processed", lang, mafiles_count) + "\n"
        
        if errors:
            result_message += "\n" + get_text("errors_processing", lang) + "\n"
            for error in errors[:5]:  # Show only first 5 errors
                result_message += f"- {error}\n"
            
            if len(errors) > 5:
                result_message += get_text("more_errors", lang, len(errors) - 5)
        
        await update.message.reply_text(
            result_message,
            reply_markup=get_main_keyboard(context)
        )
    
    else:
        # Unknown file type
        await update.message.reply_text(
            get_text("unsupported_file", lang),
            reply_markup=get_main_keyboard(context)
        )
    
    return MAIN_MENU 