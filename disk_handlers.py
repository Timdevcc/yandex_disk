import os
import requests


def get_disk_info(oauth: str) -> dict:
    """Возвращает словарь с общей информацией о диске пользователя

    https://yandex.ru/dev/disk/api/reference/capacity.html

    :param oauth: OAuth токен пользователя
    """
    url = "https://cloud-api.yandex.net/v1/disk/"
    headers = {
        "Authorization": "OAuth " + oauth
    }
    response = requests.get(url, headers=headers)
    return response.json()


def get_file_or_dir_metainfo(oauth: str, path: str, fields='', limit=20, offset=0, sort='') -> dict:
    """Возвращает словарь с метаинформацией о файле или папке

    https://yandex.ru/dev/disk/api/reference/meta.html

    :param oauth: OAuth Пользователя
    :param path: Путь до файла или папки
    :param fields: Список свойств JSON, которые следует включить в ответ.
        Ключи, не указанные в этом списке, будут отброшены при составлении ответа.
        Если параметр не указан, ответ возвращается полностью, без сокращений.
        Имена ключей следует указывать через запятую, а вложенные ключи разделять точками.
        Например: name,_embedded.items.path.
    :param limit: Количество ресурсов, вложенных в папку, описание которых следует вернуть в ответе
    :param offset: Количество вложенных в папку ресурсов, которые следует
        опустить в ответе (например, для постраничного вывода). Список сортируется
        согласно значению параметра sort.
        Допустим, папка /foo содержит три файла. Если запросить метаинформацию о
        папке с параметром offset=1, API Диска вернет только описания второго и третьего файла.
    :param sort: Атрибут, по которому нужно сортировать список ресурсов, вложенных в папку
        Возможные значения: 'name', 'path', 'created', 'modified', 'size'
        Для сортировки в обратном порядке добавьте дефис к значению параметра
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources?"
    if path:
        url += 'path=' + path
    if fields:
        url += '&fields=' + fields
    if limit != 20:
        url += '&limit=' + str(limit)
    if offset:
        url += '&offset=' + str(offset)
    if sort:
        url += '&sort=' + sort

    headers = {
        "Authorization": "OAuth " + oauth
    }
    response = requests.get(url, headers=headers)
    return response.json()


def get_all_files(oauth: str, limit=20, media_type='', offset='', fields='') -> dict:
    """Возвращает словарь с одним ключом items, по этому ключу находится
    список всех файлов диска

    https://yandex.ru/dev/disk/api/reference/all-files.html

    :param oauth: OAuth пользователя
    :param limit: Количество файлов, описание которых следует вернуть в ответе.
        (по умолчанию 20)
    :param media_type: Тип файлов, которые нужно включить в список.
        Диск определяет тип каждого файла при загрузке. Чтобы запросить
        несколько типов файлов, можно перечислить их в значении параметра
        через запятую. Например, media_type="audio,video".
        Возможные значения: 'audio', 'backup', 'book', 'compressed', 'data',
        'development', 'diskimage', 'document', 'encoded', 'executable',
        'flash', 'font', 'image', 'settings', 'spreadsheet', 'text', 'unknown'
        , 'video', 'web'
    :param offset: Количество ресурсов с начала списка, которые следует
        опустить в ответе.
    :param fields: Список свойств JSON, которые следует включить в ответ.
        Ключи, не указанные в этом списке, будут отброшены при составлении ответа"""

    headers = {
        "Authorization": "OAuth " + oauth
    }

    url = "https://cloud-api.yandex.net/v1/disk/resources/files?"
    if limit != 20:
        url += "limit=" + str(limit)
    if media_type:
        url += '&' * url.count('=') + "media_type=" + media_type
    if offset:
        url += '&' * url.count('=') + "offset=" + offset
    if fields:
        url += '&' * url.count('=') + "fields=" + fields

    response = requests.get(url, headers=headers)

    return response.json()


def get_last_uploaded(oauth: str, limit=20, media_type='', fields='') -> dict:
    """Возвращает словарь с одним ключом items, по которому находится
    список последних файлов, загруженных на Диск

    https://yandex.ru/dev/disk/api/reference/recent-upload.html

    :param oauth: OAuth пользователя
    :param limit: Количество последних загруженных файлов, описание которых
        следует вернуть в ответе. (по умолчанию 20)
    :param media_type: Тип файлов, которые нужно включить в список. Диск
        определяет тип каждого файла при загрузке. Чтобы запросить несколько типов
        файлов, можно перечислить их в значении параметра через запятую.
        Например, media_type="audio,video".
        Возможные значения: 'audio', 'backup', 'book', 'compressed', 'data',
        'development', 'diskimage', 'document', 'encoded', 'executable',
        'flash', 'font', 'image', 'settings', 'spreadsheet', 'text', 'unknown'
        , 'video', 'web'
    :param fields: Список свойств JSON, которые следует включить в ответ.
        Ключи, не указанные в этом списке, будут отброшены при составлении ответа
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/last-uploaded?"
    if limit != 20:
        url += "limit=" + str(limit)
    if media_type:
        url += '&' * url.count('=') + "media_type=" + media_type
    if fields:
        url += '&' * url.count('=') + "fields=" + fields

    headers = {
        "Authorization": "OAuth " + oauth
    }

    response = requests.get(url, headers=headers)
    return response.json()


def add_metainfo(oauth: str, path, custom_properties: dict, fields='') -> dict:
    """
    !!! НА ДАННЫЙ МОМЕНТ НЕ РАБОТАЕТ !!!

    Для любого файла или папки, доступной на запись, можно задать
    дополнительные произвольные атрибуты. Эти атрибуты будут возвращаться в
    ответ на все запросы метаинформации о ресурсах

    Если запрос был обработан без ошибок, возвращает метаинформацию о запрошенном ресурсе

    Если запрос вызвал ошибку, возвращает описание ошибки.

    https://yandex.ru/dev/disk/api/reference/meta-add.html

    :param oauth: OAuth пользователя
    :param path: Путь к нужному ресурсу относительно корневого каталога Диска.
        Путь к ресурсу в Корзине следует указывать относительно корневого каталога Корзины.
    :param fields: Список свойств JSON, которые следует включить в ответ.
        Ключи, не указанные в этом списке, будут отброшены при составлении ответа.
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources?"
    if path:
        url += "path=" + path
    if fields:
        url += "&fields=" + fields

    headers = {
        "Authorization": "OAuth " + oauth
    }
    data = {
        "custom_properties": custom_properties
    }
    response = requests.patch(url, data=data, headers=headers)
    return response.json()


def upload_file(oauth: str, path: str, file_name: str, overwrite="false"):
    """Загружает файл на Диск

    https://yandex.ru/dev/disk/api/reference/upload.html

    :param oauth: OAuth пользователя
    :param path: Путь, по которому нужно загрузить файл. Не содержит имя файла
    :param file_name: Имя файла
    :param overwrite: Признак перезаписи файла. Учитывается, если файл
        загружается в папку, в которой уже есть файл с таким именем. Допустимые значения:
        false — не перезаписывать файл, отменить загрузку (используется по умолчанию);
        true — удалить файл с совпадающим именем и записать загруженный файл.
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    url = url + '?path=' + path + '/' + file_name
    if overwrite == "true":
        url += '&overwrite=' + overwrite
    headers = {
        "Authorization": "OAuth " + oauth
    }
    response = requests.get(url, headers=headers)

    if response:
        response2 = requests.put(url=response.json()["href"],
                                 data=open("downloaded/" + file_name, 'rb'))
        return {"status": "success"} if response2 else response2

    return response.json()


def upload_file_from_url(oauth: str, file_url: str, path: str, file_name='', disable_redirects="false"):
    """
    Загружает файл из URL на Диск

    https://yandex.ru/dev/disk/api/reference/upload-ext.html

    :param oauth: OAuth пользователя
    :param file_url: Ссылка на скачиваемый файл. Максимальная длина имени
        загружаемого файла — 255 символов; максимальная длина пути — 32760
        символов. Должен оканчиваться разрешением файла
    :param path: Путь на Диске, по которому должен быть доступен скачанный файл. Не содержит имя файла
    :param file_name: Имя файла. Если не указано, используется имя из URL
    :param disable_redirects: Параметр помогает запретить редиректы по адресу,
        заданному в параметре url. Допустимые значения: 'false' — обнаружив
        редирект, Диск должен скачать файл с нового адреса. Это значение используется по умолчанию.
        'true' — обнаружив редирект, Диск не должен переходить по нему и что-либо скачивать.
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    if not file_name:
        file_name = file_url[file_url.rfind('/') + 1:]
    print(file_name)
    url = url + '?url=' + file_url + '&path=' + path + '/' +  file_name
    if disable_redirects == "true":
        url = url + '&disable_redirects=' + disable_redirects

    headers = {
        "Authorization": "OAuth " + oauth
    }

    response = requests.post(url, headers=headers)

    if not response:
        return response.json()

    if response.status_code == 202:
        href = response.json()["href"]
        status = requests.get(href, headers=headers).json()
        while status["status"] != 'success':
            status = requests.get(href, headers=headers).json()

    return {'status': 'success'}


def load_file_from_disk(oauth: str, path: str, fields=''):
    """Скачивает файл с Диска в папку downloaded

    https://yandex.ru/dev/disk/api/reference/content.html

    :param oauth: OAuth пользователя
    :param path: Путь до файла на Диске
    :param fields: Список свойств JSON, которые следует включить в ответ
        Имена ключей следует указывать через запятую, а вложенные ключи
        разделять точками. Например: name,_embedded.items.path
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/download"
    url = url + '?path=' + path
    if fields:
        url += '&fields=' + fields

    headers = {
        "Authorization": "OAuth " + oauth
    }

    response = requests.get(url, headers=headers)
    if not response:
        return response
    resp_json = response.json()
    href = resp_json["href"]
    resp_json = response.json()

    response2 = requests.get(href)

    filename = path[path.rfind('/'):]
    if not os.path.isfile('downloaded/' + filename):
        with open('downloaded/' + filename, 'wb') as downloaded_file:
            downloaded_file.write(response2.content)
    else:
        filename = filename[:filename.rfind('.')] + '(1).png'
        i = 1
        while os.path.isfile('downloaded/' + filename):
            i += 1
            filename = filename[:filename.rfind('(')] + f" ({i}).png"
            print(f"{filename[:filename.rfind('(')]=}")
        print(f"{filename=}")
        with open('downloaded/' + filename,
                  'wb') as downloaded_file:
            downloaded_file.write(response2.content)
    return {'status': 'success'}


def copy(oauth: str, source_path: str, to_path: str, overwrite='false', fields=''):
    """Копирует файл или папку на Диске. Возвращает {"status": "success"}, когда копирование завершено

    https://yandex.ru/dev/disk/api/reference/copy.html

    :param oauth: OAuth пользователя
    :param source_path: Путь к файлу на Диске, который будет скопирован
    :param to_path: Путь, по которому будет скопирован файл. Содержит имя файла
    :param overwrite: Признак перезаписи. Учитывается, если ресурс копируется
        в папку, в которой уже есть ресурс с таким именем.
    :param fields: Список свойств JSON, которые следует включить в ответ

    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/copy"
    url = url + '?from=' + source_path + '&path=' + to_path
    url = url + '&overwrite=' + overwrite
    if fields:
        url = url + '&fields=' + fields

    headers = {
        "Authorization": "OAuth " + oauth
    }

    response = requests.post(url=url, headers=headers)

    if not response:
        return response.json()

    if response.status_code == 202:
        href = response.json()["href"]
        status = requests.get(href, headers=headers).json()
        while status["status"] != 'success':
            status = requests.get(href, headers=headers).json()

    return {'status': 'success'}


def move(oauth: str, source_path: str, to_path: str, overwrite="false", fields=''):
    """Перемещает файл или папку на Диске. Возвращает {"status": "success"}, когда перемещение завершено

    https://yandex.ru/dev/disk/api/reference/move.html

    :param oauth: OAuth пользователя
    :param source_path: Путь к файлу на Диске, который будет скопирован
    :param to_path: Путь, по которому будет скопирован файл. Содержит имя файла
    :param overwrite: Признак перезаписи. Учитывается, если ресурс копируется
        в папку, в которой уже есть ресурс с таким именем.
    :param fields: Список свойств JSON, которые следует включить в ответ

    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/move"
    url = url + '?from=' + source_path + '&path=' + to_path
    url = url + '&overwrite=' + overwrite
    if fields:
        url = url + '&fields=' + fields

    headers = {
        "Authorization": "OAuth " + oauth
    }

    response = requests.post(url=url, headers=headers)

    if not response:
        return response.json()

    if response.status_code == 202:
        href = response.json()["href"]
        status = requests.get(href, headers=headers).json()
        while status["status"] != 'success':
            status = requests.get(href, headers=headers).json()

    return {'status': 'success'}


def delete(oauth: str, path: str, permanently='false', fields=''):
    """Удаляет файл или папку или перемещает его в корзину Диска

    https://yandex.ru/dev/disk/api/reference/delete.html

    :param oauth: OAuth пользователя
    :param path: Путь к удаляемому ресурсу
    :param permanently: Признак безвозвратного удаления. Поддерживаемые значения:
        false — удаляемый файл или папка перемещаются в Корзину (используется по умолчанию).
        true — файл или папка удаляются без помещения в Корзину.
    :param fields: Список свойств JSON, которые следует включить в ответ

    :return: {"status": "success"} если удачно, иначе словарь с кодом ответа и причной
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources"
    url = url + "?path=" + path
    url = url + '&permanently=' + permanently
    if fields:
        url = url + '&fields=' + fields

    headers = {
        "Authorization": "OAuth " + oauth
    }

    response = requests.delete(url=url, headers=headers)

    if not response:
        return response.json()

    if response.status_code == 202:
        href = response.json()["href"]
        status = requests.get(href, headers=headers).json()
        while status["status"] != "success":
            status = requests.get(href, headers=headers).json()

    return {"status": "success"}


def create_folder(oauth: str, path: str, fields=''):
    """Создает папку на Диске

    https://yandex.ru/dev/disk/api/reference/create-folder.html

    :param oauth: OAuth пользователя
    :param path: Путь к создаваемой папке
    :param fields: Список свойств JSON, которые следует включить в ответ.

    :return Если запрос был обработан без ошибок, возвращается ссылка на
        мета-информацию о созданном ресурсе. При ошибке обработки возвращается
        подходящий код ответа, а тело ответа содержит описание ошибки.
        Пример: {
                    "href": "https://cloud-api.yandex.net/v1/disk/resources?path=...",
                    "method": "GET",
                    "templated": false}

    """

    url = "https://cloud-api.yandex.net/v1/disk/resources" + '?path=' + path
    if fields:
        url = url + "&fields=" + fields

    headers = {
        "Authorization": "OAuth " + oauth
    }

    response = requests.put(url=url, headers=headers)
    return response.json()


def trash_delete(oauth: str, path=''):
    """Удаляет файл или папку из корзины. Если путь не указан, очищает корзину

    !!! НА ДАННЫЙ МОМЕНТ НЕЛЬЗЯ УДАЛИТЬ КОНКРЕТНЫЙ ФАЙЛ, ТОЛЬКО КОРЗИНУ ЦЕЛИКОМ!!!

    https://yandex.ru/dev/disk/api/reference/trash-delete.html

    :param oauth: OAuth пользователя
    :param path: Путь к удаляемому ресурсу относительно корневого каталога Корзины
    """

    url = "https://cloud-api.yandex.net/v1/disk/trash/resources"
    if path:
        url = url + "?path=" + path

    headers = {
        "Authorization": "OAuth " + oauth
    }

    response = requests.delete(url=url, headers=headers)

    if not response:
        return response.json()

    if response.status_code == 202:
        href = response.json()["href"]
        status = requests.get(href, headers=headers).json()
        while status["status"] != 'success':
            status = requests.get(href, headers=headers).json()

    return {"status": "success"}


def restore(oauth: str, path: str, name='', overwrite='false'):
    """
    !!! НА ДАННЫЙ МОМЕНТ НЕ РАБОТАЕТ !!!

    Восстанавливает файл из Корзины на прежнее место. Если
    восстанавливаемый файл находился внутри папки, которая отсутствует на
    момент запроса, эта папка будет создана на прежнем месте

    https://yandex.ru/dev/disk/api/reference/trash-restore.html

    :param oauth: OAuth пользователя
    :param path: Путь к восстанавливаемому ресурсу относительно корневого каталога Корзины
    :param name: Новое имя восстанавливаемого ресурса.
    :param overwrite: Признак перезаписи. 'true' или 'false'
    """

    url = "https://cloud-api.yandex.net/v1/disk/trash/resources/restore"
    url = url + '?path=' + path
    if name:
        url = url + '&name=' + name
    url = url + '&overwrite=' + overwrite

    headers = {
        "Authorization": "OAuth " + oauth
    }

    response = requests.put(url=url, headers=headers)

    if not response:
        return response.json()

    if response.status_code == 202:
        href = response.json()["href"]
        status = requests.get(href).json()
        while status["status"] != 'success':
            status = requests.get(href).json()

    return {'status': 'success'}


def get_filenames_list(oauth: str, limit=20, media_type='', offset='') -> list:
    """Возвращает плоский список всех файлов на Диске

    :param oauth: OAuth пользователя
    :param limit: Количество файлов, описание которых следует вернуть в ответе
    :param media_type: Тип файлов, которые нужно включить в список.
        Чтобы запросить несколько типов файлов, можно перечислить их в
        значении параметра через запятую.
    :param offset: Количество ресурсов с начала списка, которые следует опустить в ответе.
    :returns: Список всех файлов с указанным полным путём"""

    return [item["path"] for item in
            get_all_files(oauth, limit, media_type, offset)["items"]]

