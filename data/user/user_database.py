import os
import json
from threading import Lock

class UserDatabase:
    _instance = None
    _lock = Lock()
    _pattern = {"user_id": -1, "username": "name", "age": 0, "day": 0, "training_part":0, "name": "name", "weight":15, "gender": None,"training_day_started": False, "timezone":"Europe/Kyiv", "training_day_is_done":False, "message_id": 0}
    def __new__(cls):

        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        """Ініціалізація бази даних"""
        script_dir = os.path.dirname(__file__)
        self._path = os.path.join(script_dir, "user_db.json")

        if os.path.exists(self._path):
            with open(self._path, encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = {"users": []}  # Структура бази
            self.__update_db()

    def add(self, user_id: int, d: dict):
        if not any(user["user_id"] == user_id for user in self._data["users"]):
            self._data["users"].append({
                "user_id": user_id,
                "username": d["username"],
                "age": d.get("age", self._pattern["age"]),
                "day": 0,
                "name": d.get("name", self._pattern["name"]),
                "gender":d.get("gender", self._pattern["gender"]),
                "weight":d.get("weight", self._pattern["weight"]),
                "timezone": d.get("timezone", self._pattern["timezone"]),
                "training_day_started": False,
                "training_day_is_done":False,
                "training_part": 0,
                "message_id": 0
            })
            self.__update_db()
            return True

        return False

    def get(self, user_id):
        return next((user for user in self._data["users"] if user["user_id"] == user_id), None)


    def update(self, user_id, line, value):
        for user in self._data["users"]:
            if user and user["user_id"] == user_id: #and line in self._pattern:
                user[line] = value
                self.__update_db()
                return True
        return False

    def get_all(self):
        return [user for user in self._data["users"]]

    def update(self, user_id, line, value):
        for user in self._data["users"]:
            if user and user["user_id"] == user_id and line in self._pattern:
                user[line] = value
                print(f"user[{line}] = {value}")
                self.__update_db()
                return True
        return False


    def __update_db(self):
        with open(self._path, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    db1 = UserDatabase()


    db2 = UserDatabase()
    print(db2.update(434831975,"day",0))

