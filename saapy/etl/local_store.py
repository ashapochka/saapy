from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware


def open_json_db(json_file_path):
    db = TinyDB(json_file_path, storage=CachingMiddleware(JSONStorage))
    return db
