import hashlib
import logging

from rr_lib.db import DBHandler

log = logging.getLogger("users_store")

class UsersStore(DBHandler):
    def __init__(self):
        super(UsersStore, self).__init__(name='main')
        db = self.db
        if "users" not in self.collection_names:
            self.users = db.create_collection("users")
            self.users.create_index([("name", 1)], unique=True)
            self.users.create_index([("user_id", 1)], unique=True)
        else:
            self.users = db.get_collection("users")

    def get_user(self, uid):
        return self.users.find_one({"user_id":uid})

    def add_user(self, name, pwd, uid):
        log.info("add user %s %s %s" % (name, pwd, uid))
        if not self.users.find_one({"$or": [{"user_id": uid}, {"name": name}]}):
            m = hashlib.md5()
            m.update(pwd)
            crupt = m.hexdigest()
            return self.users.insert_one({"name": name, "pwd": crupt, "user_id": uid})

    def check_user(self, name, pwd):
        found = self.users.find_one({"name": name})
        if found:
            m = hashlib.md5()
            m.update(pwd)
            crupt = m.hexdigest()
            if crupt == found.get("pwd", ):
                return found.get("user_id", )

    def update_user(self, uid, data):
        self.users.update_one({"user_id":uid}, {"$set":data}, upsert=True)