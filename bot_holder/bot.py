import asyncio
import copy
import logging
import os
import re
import bot_holder.bot_functions as bot_f
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from utils.daily_notifier import Notifier
from aiogram.client.default import DefaultBotProperties  # Новий імпорт
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.utils.media_group import MediaGroupBuilder
from data.user.user_database import UserDatabase
from utils.keylib import Keyboard_Library
from data.archive.archive_helper import Archive_Helper
from data.schedule.day_schedule_handler import ScheduleDatabase
from collections import defaultdict
from bot_holder.AlbumMiddleware import AlbumMiddleware
from aiogram.types import Message, InputMediaPhoto, InputMedia, ContentType as CT

TOKEN = '6268679242:AAFV_OcK5GV8B7gaQ4B5y2FzHO8tB1o9efQ'
keylib = Keyboard_Library()
user_db = UserDatabase()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
db = UserDatabase()
archive_helper = Archive_Helper()
sch_db = ScheduleDatabase()
d_notify = Notifier(user_db)
router = Router()
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class PostState(StatesGroup):
    waiting_for_post = State()
    content = State()
    day = State()

    media = State()
    text = State()
    question = State()
    button = State()



class BasicForm(StatesGroup):
    name = State()
    age = State()
    gender = State()
    weight = State()
    sizes = State()
    timezone = State()

class Support(StatesGroup):
    name = State()
    age = State()
    gender = State()
    weight = State()
    sizes = State()

class Question(StatesGroup):
    question = State()

async def main():
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    d_notify.start()
    d_notify.schedule_notify(bot, dp.storage, user_db, sch_db, Question, archive_helper, keylib)
    dp.include_router(router)
    dp.message.middleware(AlbumMiddleware())
    await dp.start_polling(bot)




@dp.message(Command("start"))
async def start_handler(message: types.Message):
    keyboard = keylib.create_inline_keyboard([{"text":"Let's do it!","command":"auth_data"}])
    await message.answer(f"Привіт, {message.from_user.full_name}! 👋\nЯ- твій особистий тренер.",reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "auth_data")
async def start_reg(message: types.CallbackQuery, state: FSMContext):
    await bot.send_message(chat_id=message.from_user.id,text=f"""
🤝 Thank you for joining the program! 
Let’s make it official! Please fill out the details below so we can personalize your challenge experience. 
Please fill in the details below.👇
""")
    await asyncio.sleep(5)
    await bot.send_message(message.from_user.id,"Now please enter your name: ")
    await state.set_state(BasicForm.name)



#SetData==========================================================

@router.message(BasicForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)  # Сохраняем имя
    await message.answer("""
Thank you!
Now tell me how old are you?
""")
    await state.set_state(BasicForm.age)


@router.message(BasicForm.age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        await state.update_data(age=age)

        await message.answer(f"""
Your current weight:
        """)
        await state.set_state(BasicForm.weight)
    except ValueError:
        await message.answer(f"""
Wrong type!
Your age:
        """)
        await state.set_state(BasicForm.age)

@router.message(BasicForm.weight)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = int(message.text)
        await state.update_data(weight=weight)

        await message.answer(f"""
Good!
Now write down your gender:
            """)
        await state.set_state(BasicForm.gender)
    except ValueError:
        await message.answer(f"""
Wrong type for weight!
Your current weight:
            """)
        await state.set_state(BasicForm.weight)

@router.message(BasicForm.gender)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(gender=message.text)  # Сохраняем имя
    await message.answer("""
Thank you!
Now type your timezone in format 'Europe/Kiev' without quotes
""")
    await state.set_state(BasicForm.timezone)

@router.message(BasicForm.timezone)
async def process_gender(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await state.update_data(timezone=message.text)
    timezone = message.text

    if timezone is None or str(timezone).isdigit():
        await bot.send_message(chat_id=message.from_user.id,text="Please, write down correct timezone")
        await state.set_state(BasicForm.timezone)
    else:
        user_id = message.from_user.id
        name = user_data.get("name")
        age = user_data.get("age")
        weight = user_data.get("weight")
        gender = user_data.get("gender")

        keyboard = keylib.create_inline_keyboard(
            [{"text": "Begin Challenge", "command": "reg_end"}, {"command": "reg_edit", "text": "Enter again"}])
        db.add(user_id,
               {"username": f"@{message.from_user.username}", "age": age, "day": 0, "name": name, "gender": gender,
                "weight": weight, "timezone": timezone})
        await message.answer(f"""
        Your data:
        Name: {name},
        Age: {age},
        Weight: {weight}
        Gender: {gender},
        Timezone: {timezone}

        Do you want to change something?
        """, reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "reg_edit")
async def start_training(message: types.CallbackQuery, state: FSMContext):
    await bot.send_message(message.from_user.id,"Please, enter your name: ")
    await state.set_state(BasicForm.name)
#SetData==========================================================


@router.callback_query(lambda c: c.data == "reg_end")
async def start_training(message: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    user = db.get(user_id)
    await bot.send_message(chat_id=user_id, text=f"""
Thank you {user["name"]}! 🙌  
Now, let me take a moment to introduce myself, share why I decided to start this challenge, and explain what it’s all about! 🎉""")
    await asyncio.sleep(15)
    await bot.send_message(chat_id=user_id, text="""
Mini-Course: Your Kickstart to Transformation 🎥
1. Introduction: https://youtu.be/UqL7HuTokV0
    """)
    await asyncio.sleep(120)

    keyboard = keylib.create_inline_keyboard([{"text": "Start", "command": "training_day_0"}])

    await bot.send_message(chat_id=user_id,text="""
Welcome to your 30-DAY SAMURAI CHALLENGE! 😎
🤫 Here, I’ll be sharing everything you need to crush this challenge and make the next 30 days truly transformative! 

Here's what you'll get:
Exercise programs 🏋️‍♂️
Nutrition plans 🍏
Daily inspirations and tips 💪
Productivity hacks 🧠

📆 Every day, you’ll have practices and tasks designed to help you take a massive leap toward your goals. Stick with it, and the results will surprise you!

🤝 Invite your friends or partners to join — it’s even more fun, and it’ll strengthen your relationship along the way. 🫂
""",reply_markup=keyboard)


# Щоденні тренування ============================================================
@router.callback_query(lambda c: "training_day_" in c.data)
async def day_handler(message: types.CallbackQuery, state: FSMContext, data = None):
    if data is None:
        data = message.data
    user_id = message.from_user.id
    await bot_f.day_handler(bot=bot, user_id=user_id, state=state, user_db=user_db, sch_db=sch_db, Question=Question, archive_helper=archive_helper, keylib=keylib, data = data)

async def posts_handle(user_id, post, state, day):
    await bot_f.posts_handle(bot, user_id, post, state, day, user_db, sch_db, archive_helper, keylib, Question)


@router.message(Question.question)
async def process_message(message: Message, state: FSMContext):
    question = message.text
    user = user_db.get(message.from_user.id)
    await state.clear()
    command = f"training_day_{user["day"]}_{user["training_part"] + 1}"
    print(f"command: {command}")
    await day_handler(message=message, state=state, data=command)

@router.callback_query(lambda c: "quest_button_command_" in c.data)
async def day_handlerer(message: types.CallbackQuery, state: FSMContext):
    mess = message
    data = str(message.data).split("_")

    user_id = message.from_user.id
    await bot_f.day_handlerer(bot, user_id, data, state, user_db, sch_db, Question, archive_helper, keylib)

# Щоденні тренування ============================================================


#Адмінська панель ================================================================

@dp.message(F.text.startswith("/start_day_"))
async def my_command_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = user_db.get(user_id)
    if "status" in user and user["status"] == "admin":
        command_name = message.text.split("_")
        day = int(command_name[2])
        print(f"Command: {user["user_id"]}")
        user_db.update(user_id, "day", day)
        data = f"training_day_{day}"
        await asyncio.sleep(1)
        await bot_f.day_handler(bot=bot, user_id=user_id, state=state, user_db=user_db, sch_db=sch_db, Question=Question, archive_helper=archive_helper, keylib=keylib, data = data)

@router.callback_query(lambda c: "second_button_for_day" in c.data)
async def my_second_command_handler(message: types.CallbackQuery, state: FSMContext):
    user_id = message.from_user.id
    user = user_db.get(user_id)
    command_name = message.data.split("_")
    day = command_name[4]
    part = command_name[5]
    delay = float(command_name[6]) if len(command_name) > 6 else 0.2
    command = f"training_day_{user["day"]}_{part}"
    await asyncio.sleep(delay)
    await bot_f.day_handler(bot=bot, user_id=user_id, state=state, user_db=user_db, sch_db=sch_db, Question=Question, archive_helper=archive_helper, keylib=keylib, data=command)


#Додавання нового дня===================================
@dp.message(F.text.startswith("/add_day"))
async def my_command_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    post = 0
    user = user_db.get(user_id)
    command = message.text.split("_")
    st_ms = "found"
    if "status" in user and user["status"] == "admin":
        if len(command) > 2:
            day = int(command[2])
            ddd = sch_db.get_day(day)
            if ddd is None:
                day = sch_db.add(archive_helper=archive_helper, day=day)
                if not os.path.exists(os.path.join(archive_helper.rel_path, f"day_{day}")):
                    archive_helper.create_directory(day)
                st_ms = "created"
            elif ddd == []:
                if not os.path.exists(os.path.join(archive_helper.rel_path, f"day_{day}")):
                    archive_helper.create_directory(day)

            if len(command) > 3:
                post = command[3]
        else:
            day = sch_db.add(archive_helper=archive_helper)
            st_ms = "created"
            if not os.path.exists(os.path.join(archive_helper.rel_path, f"day_{day}")):
                archive_helper.create_directory(day)

        keyboard = keylib.create_inline_keyboard(
            [
            {"text": "Simple Text", "command": f"create_text_post_{day}_{post}"},
            {"text": "Media", "command": f"create_media_post_{day}_{post}"},
            {"text": "Question", "command": f"create_question_post_{day}_{post}"},
            {"text": "Button", "command": f"create_button_post_{day}_{post}"},
            ])
        message = await bot.send_message(chat_id=user_id, text=f"Day {day} has been {st_ms}!\nChoose the post type:", reply_markup=keyboard)

@router.callback_query(lambda c: re.match(r"create_\w+_post", c.data))
async def my_command_handler(message: types.CallbackQuery, state: FSMContext):
    command = message.data.split("_")
    await bot.edit_message_reply_markup(chat_id=message.from_user.id,
                                        message_id=message.message.message_id,
                                        reply_markup=None)
    await state.update_data(day=command[3])
    if command[1] == "media":
        await bot.send_message(chat_id=message.from_user.id, text=f"Now send your post")
        await state.set_state(PostState.media)
    elif command[1] == "text":
        await bot.send_message(chat_id=message.from_user.id, text=f"Now send your text")
        await state.set_state(PostState.text)
    elif command[1] == "question":
        await bot.send_message(chat_id=message.from_user.id, text=f"Now send text your question")
        await state.set_state(PostState.question)
    elif command[1] == "button":
        await bot.send_message(chat_id=message.from_user.id, text="""Now send text your message. Example:
Text of the\nmessage!\n[button1 | button2]\n[answer_to_button_1\n|\nanswer_to_button_2]\n[button_answer_on_button_1 | button_answer_on_button_2]""")
        await state.set_state(PostState.button)

@router.message(PostState.button)
async def handle_button(message: Message, state: FSMContext):
    data = await state.get_data()
    day = int(data.get("day"))
    posts = sch_db.get_day(day)
    post_id = len(posts) if posts is not None else 0

    parts = re.split(r"(\[.*)", message.html_text, maxsplit=1, flags=re.DOTALL)
    intro_text = parts[0].strip()
    buttons_text = parts[1] if len(parts) > 1 else ""

    matches = re.findall(r"\[(.*?)\]", buttons_text, re.DOTALL)
    button_texts = matches[0].split(" | ")
    button_answers = matches[1].split("\n|\n") if len(matches) > 1 else []
    answer_button = matches[2].split(" | ")  if len(matches) > 2 else []

    buttons = []

    for i, text in enumerate(button_texts):
        button_data = {"text": text.strip()}

        if i < len(button_answers):
            button_data["answer"] = button_answers[i].strip()

        if answer_button and i < len(answer_button) and answer_button[i] != "":
            button_data["answer_button"] = {"text": answer_button[i]}
        buttons.append(button_data)

    post = {
        "id": post_id,
        "addition": "button",
        "buttons": buttons,
        "text": intro_text
    }
    await state.update_data(content=post)
    await bot.send_message(chat_id=message.from_user.id, text="Done!\nNow, please, write a delay")
    await state.set_state(PostState.waiting_for_post)




    #await bot.send_message(chat_id=message.from_user.id, text=f"Result: {parsed_results}")


@router.message(PostState.media)
async def handle_albums(message: Message, album: list[Message], state: FSMContext):
    print(message.html_text)
    await state.update_data(media=True)
    data = await state.get_data()
    user_id = message.from_user.id
    media_group = []
    day = int(data.get("day"))
    day_sch = sch_db.get_day(day)
    post = {"id": len(day_sch)}
    path = []
    files = []
    for msg in album:
        if msg.photo:
            file_id = msg.photo
            files.append([file_id[-1], "image"])

        else:
            obj_dict = msg.model_dump()
            file_id = obj_dict[msg.content_type]
            files.append([file_id, "video"])


    if len(files) >= 1:
        post["addition"] = "media"
        files.sort(key=lambda x: x[1] != "image")
        await bot.send_message(chat_id=user_id, text="Files are loading, please wait...")
        paths = await download_files(bot, files, day, len(day_sch))
        path = [{"format": file["format"], "path": file["path"]} for file in paths]
        post["path"] = path
        post["text"] = message.html_text


    await bot.send_message(chat_id=user_id, text="Load has been complete!\n Now, type a delay between that post and a next one...")
    await state.update_data(day=day, content=post)
    await state.set_state(PostState.waiting_for_post)

@router.message(PostState.question)
async def handle_quest(message: Message, state: FSMContext):
    data = await state.get_data()
    day = int(data.get("day"))
    posts = sch_db.get_day(day)
    post_id = len(posts) if posts is not None else 0
    post = {"id": post_id, "addition": "question", "text": message.html_text}
    await state.update_data(content=post)
    await bot.send_message(chat_id=message.from_user.id, text="Done!\nNow, please, write a delay")
    await state.set_state(PostState.waiting_for_post)

@router.message(PostState.text)
async def handle_text(message: Message, state: FSMContext):
    data = await state.get_data()
    day = int(data.get("day"))
    posts = sch_db.get_day(day)
    post_id = len(posts) if posts is not None else 0
    post = {"id": post_id, "addition": None, "text": message.html_text}
    await state.update_data(content=post)
    await bot.send_message(chat_id=message.from_user.id, text="Now, please, write a delay")
    await state.set_state(PostState.waiting_for_post)






@router.message(PostState.waiting_for_post)
async def handle_post_general(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        post = data.get("content")
        delay = float(message.text)
        post["delay"] = delay
        sch_db.add_post(data.get("day"),archive_helper=archive_helper, content=post)
        await asyncio.sleep(5)
        print(data.get("media"))
        if data.get("media") is not None:
            archive_helper.ULTRA_MEGA_CONVERTOR(int(data.get("day")), sch_db)

        await bot.send_message(chat_id=message.from_user.id, text="Got a post!")
        await state.clear()
    except ValueError:
        await bot.send_message(chat_id=message.from_user.id, text="Wrong format")
        await state.set_state(PostState.waiting_for_post)



async def download_files(bot: Bot, files: list, day: int, post: int):
    counter = -1
    paths = []
    post = post+1
    print(f"Post id: {post}")
    if len(files) > 1:
        for index, file in enumerate(files):
            if file[1] == "image":
                path = archive_helper.create_photo_path(day,post, int(index)+1)
                await bot.download(file[0], destination=path[0])
                #print(f"path[0]:{path[0]}")
                paths.append({"format": "image", "path": path[1]})
            elif file[1] == "video":
                file_ext = "MOV"
                path = archive_helper.create_video_path(day,post, int(index)+1, file_ext)
                #print(f"path[0]:{path[0]}")
                await bot.download(file[0]["file_id"], destination=path[0])
                paths.append({"format": "video", "path": path[1]})

    elif len(files) == 1:
        file = files[0]
        if file[1] == "image":
            path = archive_helper.create_photo_path(day, post, -1)
            await bot.download(file[0], destination=path[0])
            paths.append({"format": "image", "path": path[1]})
        elif file[1] == "video":
            file_ext = "MOV"
            path = archive_helper.create_video_path(day, post, -1, file_ext)
            await bot.download(file[0]["file_id"], destination=path[0])
            paths.append({"format": "video", "path": path[1]})
    return paths


@dp.message(F.text.startswith("/upd"))
async def my_command_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = user_db.get(user_id)
    if "status" in user and user["status"] == "admin":
        sch_db.adm_update()
        await bot.send_message(chat_id=user_id,text="DB has been updated!")


#Додавання нового дня ================================================

#Адмінська панель ================================================================





if __name__ == "__main__":
    asyncio.run(main())
    #keyboard = keylib.create_inline_keyboard([{"text":"Start Day 1","command":"training_day_1"}])

