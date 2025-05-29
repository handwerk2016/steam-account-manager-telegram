import logging
import json
from telegram import Update, InputFile
from telegram.ext import ContextTypes, ConversationHandler
from utils.decorators import restricted
from utils.message_formatter import get_main_keyboard
from utils.file_handlers import create_asf_configs_zip
from utils.localization import get_text, get_user_language
from handlers.command_handlers import MAIN_MENU, WAITING_FOR_TEMPLATE

# States for ConversationHandler
# WAITING_FOR_TEMPLATE = 5  # Defined in command_handlers.py

@restricted
async def start_asf_config_generation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the ASF config generation process"""
    lang = get_user_language(context)
    
    # Save current state in user_data
    context.user_data['state'] = WAITING_FOR_TEMPLATE
    
    await update.message.reply_text(
        get_text("send_asf_template", lang),
        reply_markup=get_main_keyboard(context)
    )
    
    return WAITING_FOR_TEMPLATE

@restricted
async def process_asf_template(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes text message with ASF config template"""
    text = update.message.text.strip()
    lang = get_user_language(context)
    
    # Reset state in user_data
    context.user_data['state'] = MAIN_MENU
    
    try:
        # Check that text is valid JSON
        template_content = text
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