import os
import json
import time
from threading import Lock
#from data.archive.archive_helper import Archive_Helper


class ScheduleDatabase:
    _instance = None
    _lock = Lock()
    def __new__(cls):

        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        """Ініціалізація бази даних"""
        self.__script_dir = os.path.dirname(__file__)
        self._path = os.path.join(self.__script_dir, "schedule_db.json")

        if os.path.exists(self._path):
            with open(self._path, encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = {"day_0": []}  # Структура бази
            self.__update_db()

    def add(self, d:list=None, archive_helper=None, day = 1):
            day = day if day > 1 else len(self._data)
            if d is None:
                d = []
            self._data[f"day_{day}"] = d
            self.__update_db()
            return int(day)

    def add_post(self,day, archive_helper, content: dict=None):
        dd = self.get_day(day)
        if dd is None:
            self.add(archive_helper=archive_helper)
            time.sleep(0.2)
            day = self.get_day(day)
        try:
            print(f"get_day = {day}")
            self._data[f"day_{day}"].append(content)
            self.__update_db()
            return True
        except TypeError:
            return False


    def update_video_extensions(self, day: int):
            for post in self._data[f"day_{day}"]:
                #print(f'if post["addition"] == "media": {post["addition"] == "media"}')
                if post["addition"] == "media":
                    print(f'')
                    for f in post["path"]:
                        if f['format'] == "video":
                            print(f'{f['path']} -> {f['path'].replace("MOV", "mp4")}')
                            f['path'] = f['path'].replace("MOV", "mp4")
            self.__update_db()

    def get_day(self, day):
        if f"day_{day}" in self._data:
            return self._data[f"day_{day}"]
        else:
            return None

    def adm_update(self):
        self.__update_db()


    def __update_db(self):
        with open(self._path, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    db1 = ScheduleDatabase()
    #db1.update_video_extensions(day=2)
    #a_h = Archive_Helper()
    #print(db1.add(archive_helper=a_h))
    #db2 = ScheduleDatabase()
    #print(db2.update(1,"day",0))

