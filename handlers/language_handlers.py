import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from utils.decorators import restricted
from utils.localization import get_language_keyboard, set_user_language, get_text, get_user_language
from utils.message_formatter import get_main_keyboard
from handlers.command_handlers import MAIN_MENU

@restricted
async def show_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Показывает меню выбора языка"""
    lang = get_user_language(context)
    
    # Сохраняем текущее состояние в user_data
    # Сохраняем предыдущее состояние, чтобы вернуться к нему после выбора языка
    if 'state' in context.user_data:
        context.user_data['prev_state'] = context.user_data['state']
    else:
        context.user_data['prev_state'] = MAIN_MENU
    
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            get_text("select_language", lang),
            reply_markup=get_language_keyboard()
        )
    else:
        await update.message.reply_text(
            get_text("select_language", lang),
            reply_markup=get_language_keyboard()
        )
    
    return MAIN_MENU

@restricted
async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает выбор языка"""
    query = update.callback_query
    await query.answer()
    
    # Извлекаем код языка из callback_data
    lang_code = query.data.split("_")[1]
    
    # Устанавливаем язык пользователя
    if set_user_language(context, lang_code):
        # Получаем текст на новом языке
        lang_changed_text = get_text("language_changed", lang_code)
        
        # Отправляем сообщение о смене языка
        await query.edit_message_text(lang_changed_text)
        
        # Отправляем новое сообщение с клавиатурой на новом языке
        await query.message.reply_text(
            get_text("choose_action", lang_code),
            reply_markup=get_main_keyboard(context)
        )
    else:
        # Если язык не поддерживается, отправляем сообщение об ошибке
        await query.edit_message_text(
            "Unsupported language / Неподдерживаемый язык"
        )
    
    return MAIN_MENU 