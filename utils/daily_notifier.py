from apscheduler.schedulers.asyncio import AsyncIOScheduler
from data.user.user_database import UserDatabase
from aiogram import Bot
import pytz
from datetime import datetime, timedelta
import asyncio
import bot_holder.bot_functions as bot_functions


class Notifier:
    def __init__(self, db: UserDatabase = UserDatabase()):
        self.db = db
        self.scheduler = AsyncIOScheduler()

    def get_next_reminder_datetime(self, reminder_time_str, tz_str):
        tz = pytz.timezone(tz_str)
        now = datetime.now(tz)
        reminder_time = datetime.strptime(reminder_time_str, "%H:%M").time()
        reminder_dt = datetime.combine(now.date(), reminder_time)
        reminder_dt = tz.localize(reminder_dt)
        if reminder_dt <= now:
            reminder_dt += timedelta(days=1)
        return reminder_dt

    async def notify(self, bot, state, user_id, user_db, sch_db, Question, archive_helper, keylib):
        user = user_db.get(user_id)
        command = f"training_day_{user['day']+1}_0"
        print(user)
        await bot_functions.day_handler(bot,  user_id, state, user_db, sch_db, Question, archive_helper, keylib, data=command)

    def schedule_notify(self, bot: Bot, state, user_db, sch_db, Question, archive_helper, keylib):
        users = self.db.get_all()
        for user in users:
            user_id = user["user_id"]
            timezone = user.get("timezone", "Europe/Kiev")
            reminder_time = "12:20" #(datetime.now() + timedelta(minutes=1)).strftime("%H:%M") #Время, когда бот запускается в зависимости от пояса

            reminder_dt = self.get_next_reminder_datetime(reminder_time, timezone)
            utc_dt = reminder_dt.astimezone(pytz.utc) + timedelta(seconds=5)

            print(f"🔹 Заплановано для {user_id} о {utc_dt} UTC (поточний: {datetime.utcnow()} UTC)")

            try:
                self.scheduler.add_job(
                    self.notify,
                    trigger="date",
                    run_date=utc_dt,
                    args=[bot, state, user_id, user_db, sch_db, Question, archive_helper, keylib],
                    id=f"notify_{user_id}_{utc_dt}",
                )
                print(f"✅ Завдання для {user_id} успішно додано!")
            except Exception as e:
                print(f"❌ Помилка при додаванні завдання: {e}")

    def start(self):
        self.scheduler.start()
        print("⏳ APScheduler запущено... Очікуємо подій...")
        asyncio.create_task(self.keep_alive())

    async def keep_alive(self):
        while True:
            await asyncio.sleep(60)  # Запобігає завершенню event loop
