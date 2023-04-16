import logging
import os
import disk_handlers
from config import TG_TOKEN, Y_CLIENTID
from data import db_session
from telegram import ForceReply, Update, ReplyKeyboardMarkup, File
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
import Bot_Handler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    bot = Bot_Handler.Bot_handler()
    application = Application.builder().token(TG_TOKEN).build()
    global db_sess
    db_sess = db_session.create_session()
    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', bot.start)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_token)]
            
        },
        fallbacks=[CommandHandler('stop', bot.stop)]
    )

    upload_handler = ConversationHandler(
        entry_points=[CommandHandler("upload_file", bot.upload_file)],
        states={
            1: [MessageHandler(filters.ALL, bot.get_path)],
            2: [MessageHandler(filters.ALL, bot.uploaded_file)]
        },
        fallbacks=[CommandHandler("stop", bot.stop)]
    )

    update_handler = ConversationHandler(
        entry_points=[CommandHandler('update_token', bot.update_token)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_token)]
            
        },
        fallbacks=[CommandHandler('stop', bot.stop)]
    )

    folder_handler = ConversationHandler(
        entry_points=[CommandHandler('create_folder', bot.create_folder)],
        states={
            1: [MessageHandler(filters.ALL, bot.get_path)],
            2: [MessageHandler(filters.ALL, bot.created_folder)]
        },
        fallbacks=[CommandHandler('stop', bot.stop)]
    )

    download_file = ConversationHandler(
        entry_points=[CommandHandler("download_file", bot.download_file)],
        states={
            1: [MessageHandler(filters.ALL, bot.get_path)]
        },
        fallbacks=[CommandHandler('stop', bot.stop)]
    )

    delete_handler = ConversationHandler(
        entry_points=[CommandHandler("delete_file", bot.delete_file)],
        states={
            1: [MessageHandler(filters.ALL, bot.get_path)]
        },
        fallbacks=[CommandHandler('stop', bot.stop)]
    )

    copy_handler = ConversationHandler(
        entry_points=[CommandHandler("copy", bot.copy)],
        states={
            1: [MessageHandler(filters.ALL, bot.get_path)],
        },
        fallbacks=[CommandHandler('stop', bot.stop)]
    )
    application.add_handler(CommandHandler("get_all_files", bot.get_all_files))
    application.add_handler(CommandHandler("get_disk_info", bot.get_disk_info))
    application.add_handler(CommandHandler('clear_trash_bin', bot.clear_trash_bin))
    application.add_handler(copy_handler)
    application.add_handler(folder_handler)
    application.add_handler(upload_handler)
    application.add_handler(download_file)
    application.add_handler(start_handler)
    application.add_handler(update_handler)
    application.add_handler(delete_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
