import os

from telegram import ForceReply, Update, ReplyKeyboardMarkup, File
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from data import db_session
from data.users import User
import disk_handlers
from config import TG_TOKEN, Y_CLIENTID


db_session.global_init("db/users.db")
db_sess = db_session.create_session()
reply_keyboard = [["/update_token"], ["/get_all_files", '/get_disk_info'], ["/upload_file", "/download_file", "/create_folder"],
                  ["/clear_trash_bin"]]
ready_keyboard = [["/ready"]]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
ready_markup = ReplyKeyboardMarkup(ready_keyboard, one_time_keyboard=False)
get_code_url = 'https://oauth.yandex.ru/authorize?response_type=token&client_id=' + Y_CLIENTID


def byt(size):  # перевод байтов в удобную сисетму
    if size // (1024 * 1024 * 1024) >= 1:
        return str(round(size / 2 ** 30)) + "ГБ"
    elif size // 2 ** 20 >= 1:
        return str(round(size / 2 ** 20)) + "МБ"
    elif size // 1024 >= 1:
        return str(round(size / 1024)) + "КБ"
    return str(size) + "Б"


def get_user(id):
    user = db_sess.get(User, id)
    return user


class Bot_handler:
    async def start(self, update, context):
        id = update.message.chat.id
        user = get_user(id)
        if not user:
            await update.message.reply_text(f'''Приветствуй,\nЯ пока не имею  доступ к вашему Яндекс диску.
                                               \nПерейдите по ссылке, скопируйте токен и отправте мне, что я смог взаимоде́йствовать с вашим диском\n{get_code_url}''')
            return 1
        else:
            await update.message.reply_text("Бот готов к использованию", reply_markup=markup)

    async def get_token(self, update, context):
        id = update.message.chat.id
        token = update.message.text
        user = get_user(id)
        if user:
            db_sess.delete(user)

        user = User(id=id, token=token)
        db_sess.add(user)
        db_sess.commit()

        await update.message.reply_text("Ваш token был обновлен. Вы можете в любое время именить его",
                                        reply_markup=markup)

    async def stop(self, update, context):
        await update.message.reply_text("stop")

    async def update_token(self, update, context):
        await update.message.reply_text(f"Отправьте новый токен {get_code_url}")
        return 1

    async def get_path(self, update, context):
        user = get_user(update.message.chat.id)
        path = context.user_data["path"]
        typ = context.user_data["typ"]
        text = update.message.text

        if path == "disk:/":
            path = "disk:"

        if text == "/ready":
            if typ == "dir":
                await update.message.reply_text("Напишите имя")
            return 2

        if text in context.user_data["dirs"]:
            path = path + "/" + text
            context.user_data["path"] = path
            resp = disk_handlers.get_file_or_dir_metainfo(user.token, path)
            context.user_data["dirs"] = []
            for i in resp['_embedded']["items"]:
                if typ == "dir":
                    if i["type"] == "dir":
                        context.user_data["dirs"].append(i["name"])
                        await update.message.reply_text(i["name"])
                else:
                    await update.message.reply_text(i["name"])
                    if i["type"] == "dir":
                        context.user_data["dirs"].append(i["name"])
            return 1
        else:
            path = path + "/" + text
            if typ == "get_file":
                await self.downloaded_file(update, path, user.token)
                return ConversationHandler.END
            return 2

    async def downloaded_file(self, update, path, token):
        resp = disk_handlers.load_file_from_disk(token, path)
        if resp["status"] == "success":
            await update.message.reply_document(document=open(f'downloaded/{resp["filename"]}', 'rb'))
            os.remove(f"downloaded/{resp['filename']}")
        else:
            await update.message.reply_text(resp["status"])

    async def get_all_files(self, update, context):
        user = get_user(update.message.chat.id)
        resp = disk_handlers.get_all_files(user.token)
        for i in resp["items"]:
            path = i["path"].split("/")
            path.pop()
            path = "/".join(path)
            await update.message.reply_text(f"Имя файла: {i['name']}\n Путь к фалу: {path}", reply_markup=markup)

    async def upload_file(self, update, context):
        user = get_user(update.message.chat.id)

        await update.message.reply_text("Выберите папку")
        path = "disk:/"
        context.user_data["path"] = path
        context.user_data["typ"] = "dir"
        resp = disk_handlers.get_file_or_dir_metainfo(user.token, path)
        context.user_data["dirs"] = []
        for i in resp['_embedded']["items"]:
            if i["type"] == "dir":
                context.user_data["dirs"].append(i["name"])
                await update.message.reply_text(i["name"], reply_markup=ready_markup)
        return 1

    async def clear_trash_bin(self, update, contetx):
        user = get_user(update.message.chat.id)
        resp = disk_handlers.trash_delete(user.token)
        if resp.get("status") == "success":
            await update.message.reply_text("Корзина удалена")

    async def created_folder(self, update, context):
        user = get_user(update.message.chat.id)
        path = context.user_data["path"]
        path = path + "/" + update.message.text
        resp = disk_handlers.create_folder(user.token, path)
        if resp.get("href", 0) != 0:
            await update.message.reply_text("Папка была создана")
        else:
            await update.message.reply_text("Что-то пошло не так")

    async def create_folder(self, update, context):
        user = get_user(update.message.chat.id)
        path = "disk:/"
        context.user_data["path"] = path
        context.user_data["typ"] = "dir"
        await update.message.reply_text("Выберите папку, в которой вы хотите создать папку")
        context.user_data["dirs"] = []
        resp = disk_handlers.get_file_or_dir_metainfo(user.token, path)
        for i in resp['_embedded']["items"]:
            if i["type"] == "dir":
                context.user_data["dirs"].append(i["name"])
                await update.message.reply_text(i["name"], reply_markup=ready_markup)
        return 1

    async def uploaded_file(self, update, context):
        user = get_user(update.message.chat.id)
        path = context.user_data["path"]
        message = update.message
        attachment = message.effective_attachment

        if type(attachment) == tuple:
            new_file = await attachment[-1].get_file()
        else:
            new_file = await attachment.get_file()
        await new_file.download_to_drive('downloaded/file')
        print(path)
        resp = disk_handlers.upload_file(user.token, path, "file")
        if resp.get("status", 0) == "success":
            await update.message.reply_text("Файл был удачно загружен", reply_markup=markup)
        else:
            await update.message.reply_text(resp["message"], reply_markup=markup)
        return ConversationHandler.END

    async def download_file(self, update, context):
        user = get_user(update.message.chat.id)

        await update.message.reply_text("Выберите файл.\nЕсли вы хотите перейти к какой-то папке, то отправтье ее название")
        path = "disk:/"
        context.user_data["path"] = path
        context.user_data["typ"] = "get_file"
        resp = disk_handlers.get_file_or_dir_metainfo(user.token, path)
        context.user_data["dirs"] = []
        for i in resp['_embedded']["items"]:
            if i["type"] == "dir":
                context.user_data["dirs"].append(i["name"])
            await update.message.reply_text(i["name"])
        return 1

    async def get_disk_info(self, update, context):
        user = get_user(update.message.chat.id)
        resp = disk_handlers.get_disk_info(user.token)

        await update.message.reply_text(f'''Страна: {resp["user"]["country"]}, Имя пользователя {resp["user"]["display_name"]}
Общий объем Диска, доступный пользователю: {byt(resp["total_space"])}
Объем файлов, находящихся в Корзине: {byt(resp["trash_size"])}
Объем файлов, хранящихся на Диске: {byt(resp["used_space"])}''')
