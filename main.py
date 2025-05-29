import logging
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    CallbackQueryHandler, 
    ConversationHandler
)
from config import BOT_TOKEN
from handlers.command_handlers import (
    start, 
    help_command,
    config_command,
    back_to_main,
    MAIN_MENU, 
    ACCOUNT_LIST, 
    ACCOUNT_DETAIL, 
    ACCOUNT_EDIT, 
    ACCOUNT_DELETE, 
    CONFIRM_DELETE_ALL,
    WAITING_FOR_TEMPLATE
)
from handlers.account_handlers import (
    show_account_list,
    show_account_detail,
    delete_account_handler,
    confirm_clear_all,
    clear_all_accounts_handler,
    cancel_clear_all,
    back_to_list,
    download_all_accounts,
    download_account
)
from handlers.message_handlers import handle_text
from handlers.document_handlers import handle_document
from handlers.language_handlers import show_language_menu, change_language
from handlers.asf_handlers import process_asf_template

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main() -> None:
    """Bot startup"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Common handlers for all states
    common_handlers = [
        MessageHandler(filters.Regex("^📋 Список аккаунтов$|^📋 Account list$"), show_account_list),
        MessageHandler(filters.Regex("^🔄 Обновить$|^🔄 Refresh$"), start),
        MessageHandler(filters.Regex("^📥 Скачать все аккаунты$|^📥 Download all accounts$"), download_all_accounts),
        MessageHandler(filters.Regex("^🗑 Очистить хранилище$|^🗑 Clear storage$"), confirm_clear_all),
        MessageHandler(filters.Regex("^📤 Импорт ZIP$|^📤 Import ZIP$"), handle_text),
        MessageHandler(filters.Regex("^🌐 Язык / Language$|^🌐 Language / Язык$"), show_language_menu),
        MessageHandler(filters.Regex("^❓ Помощь$|^❓ Help$"), help_command),
        MessageHandler(filters.Document.ALL, handle_document),
    ]
    
    # Handlers for ASF template waiting state (without document handler)
    template_handlers = [
        MessageHandler(filters.Regex("^📋 Список аккаунтов$|^📋 Account list$"), show_account_list),
        MessageHandler(filters.Regex("^🔄 Обновить$|^🔄 Refresh$"), start),
        MessageHandler(filters.Regex("^📥 Скачать все аккаунты$|^📥 Download all accounts$"), download_all_accounts),
        MessageHandler(filters.Regex("^🗑 Очистить хранилище$|^🗑 Clear storage$"), confirm_clear_all),
        MessageHandler(filters.Regex("^📤 Импорт ZIP$|^📤 Import ZIP$"), handle_text),
        MessageHandler(filters.Regex("^🌐 Язык / Language$|^🌐 Language / Язык$"), show_language_menu),
        MessageHandler(filters.Regex("^❓ Помощь$|^❓ Help$"), help_command),
    ]

    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                *common_handlers,
                CallbackQueryHandler(change_language, pattern="^lang_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
            ],
            ACCOUNT_LIST: [
                *common_handlers,
                CallbackQueryHandler(show_account_detail, pattern="^account_"),
                CallbackQueryHandler(show_account_list, pattern="^page_"),
                CallbackQueryHandler(back_to_main, pattern="^back_to_main$"),
                CallbackQueryHandler(change_language, pattern="^lang_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
            ],
            ACCOUNT_DETAIL: [
                *common_handlers,
                CallbackQueryHandler(download_account, pattern="^download_"),
                CallbackQueryHandler(delete_account_handler, pattern="^delete_"),
                CallbackQueryHandler(back_to_list, pattern="^back_to_list$"),
                CallbackQueryHandler(change_language, pattern="^lang_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
            ],
            CONFIRM_DELETE_ALL: [
                *common_handlers,
                CallbackQueryHandler(clear_all_accounts_handler, pattern="^confirm_clear_all$"),
                CallbackQueryHandler(cancel_clear_all, pattern="^cancel_clear_all$"),
                CallbackQueryHandler(change_language, pattern="^lang_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
            ],
            WAITING_FOR_TEMPLATE: [
                *template_handlers,
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_asf_template),
                MessageHandler(filters.Document.ALL, handle_document),
                CallbackQueryHandler(change_language, pattern="^lang_"),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("help", help_command),
            CommandHandler("config", config_command)
        ],
        name="account_manager_conversation",
        persistent=False,
        per_message=False,
    )

    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("config", config_command))

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main() 