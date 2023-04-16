import os

from telegram import ForceReply, Update, ReplyKeyboardMarkup, File
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from data import db_session
from data.users import User
import disk_handlers
from config import TG_TOKEN, Y_CLIENTID


db_session.global_init("db/users.db")
db_sess = db_session.create_session()
reply_keyboard = [["/update_token"], ["/get_all_files", '/get_disk_info', "/delete_file"], ["/upload_file", "/download_file", "/create_folder"],
                  ["/clear_trash", "/move", "/copy"]]
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


async def send_main_files(update, context, typ):
    user = get_user(update.message.chat.id)
    path = "disk:/"
    context.user_data["dirs"] = []
    print(typ)
    if typ == "copy1":
        context.user_data["path2"] = path
    else:
        context.user_data["path"] = path
    resp = disk_handlers.get_file_or_dir_metainfo(user.token, path)
    for i in resp['_embedded']["items"]:
        if i["type"] == "dir":
            context.user_data["dirs"].append(i["name"])
            if typ == "dir":
                await update.message.reply_text(i["name"], reply_markup=ready_markup)
            else:
                await update.message.reply_text(i["name"])
        elif typ != "dir" and typ != "copy1":
            await update.message.reply_text(i["name"])
    return 1


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
        typ = context.user_data["typ"]
        path = context.user_data["path"] if typ != "copy1" else context.user_data["path2"]
        text = update.message.text

        if path == "disk:/":
            path = "disk:"

        if text == "/ready":
            if typ == "dir":
                await update.message.reply_text("Напишите имя")
            if typ == "delete":
                await self.deleted_file(update, path)
                return ConversationHandler.END
            if typ == "copy0":
                await update.message.reply_text("Укажите путь, по которому будет скопирован файл или папка")
                context.user_data["path"] = path
                context.user_data["typ"] = "copy1"
                await send_main_files(update, context, "copy1")
                return 1
            if typ == "copy1":
                await self.copied(update, context)
                return ConversationHandler.END
            return 2

        if text in context.user_data["dirs"]:
            path = path + "/" + text
            if typ == "copy1":
                context.user_data["path2"] = path
            else:
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
            elif typ == "delete":
                await update.message.reply_text("/", reply_markup=markup)
                await self.deleted_file(update, path)
                return ConversationHandler.END
            if typ == "copy0":
                await update.message.reply_text("Укажите путь, по которому будет скопирован файл или папка")
                context.user_data["path"] = path
                context.user_data["typ"] = "copy1"
                await send_main_files(update, context, "copy1")
                return 1
            return 2

    async def copied(self, update, context):
        user = get_user(update.message.chat.id)
        path1 = context.user_data["path"]
        text = path1.split("/")[-1]
        path2 = context.user_data["path2"]
        if path2 == "disk:/":
            path2 = "disk:"
        resp = disk_handlers.copy(user.token, path2, path1)
        if resp.get("status", 0) == "success":
            await update.message.reply_text("Файл успешно скопирован")
        else:
            print(path1, path2)
            print(resp)
            await update.message.reply_text("Что-то пошло не так")

    async def copy(self, update, context):
        context.user_data["typ"] = "copy0"
        await update.message.reply_text("Укажите путь до файла или папки, который будет скопирован. Если выбрали папку, отпратье /ready",
                                        reply_markup=ready_markup)
        await send_main_files(update, context, "copy")
        return 1

    async def deleted_file(self, update, path):
        user = get_user(update.message.chat.id)
        resp = disk_handlers.delete(user.token, path)
        if resp.get("status", 0) == "success":
            await update.message.reply_text("Успешно удалено", reply_markup=markup)
        else:
            await update.message.reply_text("Что-то пошло не так", reply_markup=markup)

    async def delete_file(self, update, context):
        context.user_data["typ"] = "delete"
        await update.message.reply_text("Укажите путь для удаления файла или папки. Если выбрали папку, то отправтье /ready",
                                        reply_markup=ready_markup)
        await send_main_files(update, context, "all")
        return 1

    async def downloaded_file(self, update, path, token):
        resp = disk_handlers.load_file_from_disk(token, path)
        if resp.get("status", 1) == "success":
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
        context.user_data["typ"] = "dir"
        await send_main_files(update, context, "dir")
        return 1

    async def clear_trash_bin(self, update, contetx):
        user = get_user(update.message.chat.id)
        resp = disk_handlers.trash_delete(user.token)
        if resp.get("status") == "success":
            await update.message.reply_text("Корзина удалена")

    async def created_folder(self, update, context):
        user = get_user(update.message.chat.id)
        path = context.user_data["path"]
        if path == "disk:/":
            path = "disk:"
        path = path + "/" + update.message.text
        resp = disk_handlers.create_folder(user.token, path)
        if resp.get("href", 0) != 0:
            await update.message.reply_text("Папка была создана", reply_markup=markup)
        else:
            await update.message.reply_text("Что-то пошло не так", reply_markup=markup)
        return ConversationHandler.END

    async def create_folder(self, update, context):
        user = get_user(update.message.chat.id)
        context.user_data["typ"] = "dir"
        await update.message.reply_text("Выберите папку, в которой вы хотите создать папку")
        await send_main_files(update, context, "dir")
        return 1

    async def uploaded_file(self, update, context):
        user = get_user(update.message.chat.id)
        path = context.user_data["path"]
        if path == "disk:/":
            path = "disk:"
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
        context.user_data["typ"] = "get_file"
        await send_main_files(update, context, "get_file")
        return 1

    async def get_disk_info(self, update, context):
        user = get_user(update.message.chat.id)
        resp = disk_handlers.get_disk_info(user.token)

        await update.message.reply_text(f'''Страна: {resp["user"]["country"]}, Имя пользователя {resp["user"]["display_name"]}
Общий объем Диска, доступный пользователю: {byt(resp["total_space"])}
Объем файлов, находящихся в Корзине: {byt(resp["trash_size"])}
Объем файлов, хранящихся на Диске: {byt(resp["used_space"])}''')
