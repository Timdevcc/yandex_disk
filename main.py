import logging
import os
import requests
from telegram import __version__ as TG_VER, Bot
from config import TOKEN
from data import db_session
from data.users import User
from telegram import ForceReply, Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


reply_keyboard = [["/update_token"], ["/получить файлы"]]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


def get_user(id):
    user = db_sess.get(User, id)
    return user


get_code_url = 'https://oauth.yandex.ru/authorize?response_type=token&client_id=5bcd7b1604d1499285d37a386146fa42'


async def start(update, context):
    id = update.message.chat.id
    user = get_user(id)
    if not user:
        await update.message.reply_text(f'''Приветствуй,\nЯ пока не имею  доступ к вашему Яндекс диску.
                                           \nПерейдите по ссылке, скопируйте токен и отправте мне, что я смог взаимоде́йствовать с вашим диском\n{get_code_url}''')
        return 1
    else:
        await update.message.reply_text("Бот готов к использованию", reply_markup=markup)


async def get_token(update, context):
    id = update.message.chat.id
    token = update.message.text
    user = get_user(id)
    if user:
        db_sess.delete(user)

    user = User(id = id, token = token)
    db_sess.add(user)
    db_sess.commit()

    await update.message.reply_text("Ваш token был обновлен. Вы можете в любое время именить его", reply_markup=markup)


async def stop(update, contetx):
    await update.message.reply_text("stop")


async def update_token(update, context):
    await update.message.reply_text(f"Отпрате новый токен {get_code_url}")
    return 1


def main():
    db_session.global_init("db/users.db")
    application = Application.builder().token(TOKEN).build()
    global db_sess
    db_sess = db_session.create_session()
    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_token)]
            
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    update_handler = ConversationHandler(
        entry_points=[CommandHandler('update_token', update_token)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_token)]
            
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(start_handler)
    application.add_handler(update_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
