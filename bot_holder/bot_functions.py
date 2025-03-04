from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
import asyncio
import os
from aiogram.utils.media_group import MediaGroupBuilder
from utils.keylib import Keyboard_Library
from data.user.user_database import UserDatabase

async def day_handler(bot, user_id, state: FSMContext, user_db, sch_db, Question, archive_helper, keylib: Keyboard_Library, data = None):


    command = str(data).split("_")
    #print(f"COMMAND: {command}")

    user = user_db.get(user_id)
    day = int(command[2])
    day_qua = 3 #UPDT
    part = int(command[3]) if len(command) > 3 else 0
    print(f"Day: {day}, part: {part}, user: {user}")
    #logging.info(f"Day {day}")
    if ((day<=30 and user["training_day_is_done"] is True) or day == 1 or day >=0) and day <= day_qua:
        user_db.update(user_id, "training_day_is_done", False)
        user_db.update(user_id, "day", day)
        user_db.update(user_id, "training_day_started", True)
        posts = sch_db.get_day(day)
        #print(f"len(posts): {part}:{int(len(posts) - 1)}")
        posts_ = posts[part:]
        #print(f"posts: {posts_}")
        if part < int(len(posts) - 1):
           for post in posts_:
            await posts_handle(bot, user_id, post, state, day, user_db, sch_db, archive_helper, keylib, Question)
            if post["addition"] == "question" or post["addition"] == "button":
                break
        elif part == int(len(sch_db.get_day(day)) - 1):
            await posts_handle(bot, user_id, posts[int(len(posts) - 1)], state, day, user_db, sch_db, archive_helper, keylib, Question)

        if part == int(len(posts) - 1):
            user_db.update(user_id, "day", day+1)
            user_db.update(user_id, "training_day_is_done", True)
    elif user["training_day_is_done"] is False:
        await bot.send_message(chat_id=user_id, text="""
Hi!
You should do your homework!)""")
    elif day == 31:
        await bot.send_message(chat_id=user_id,text="")

async def posts_handle(bot, user_id, post, state, day, user_db, sch_db, archive_helper, keylib, Question):
    part = post["id"]
    print(f"post['id']: {post["id"]}")
    print(user_db.update(user_id, "training_part", part))
    if post["addition"] == "media":
        await send_m(post, archive_helper, bot, user_id, user_db)

    elif post["addition"] == "button":
        buttons = [{"text": button["text"], "command": f"quest_button_command_{day}_{post["id"]}_{indx}"} for indx, button in enumerate(post["buttons"])]
        print(buttons)
        keyboard = keylib.create_inline_keyboard(buttons)
        message = await bot.send_message(chat_id=user_id, text=post["text"], reply_markup=keyboard)
        user_db.update(user_id, "message_id", message.message_id)
    else:
        message = await bot.send_message(chat_id=user_id, text=post["text"])
        user_db.update(user_id, "message_id", message.message_id)
    if post["addition"] != "question":
        await asyncio.sleep(post["delay"])
    else:
        await state.set_state(Question.question)


async def day_handlerer(bot: Bot, user_id, data, state: FSMContext, user_db, sch_db, Question, archive_helper, keylib: Keyboard_Library):

    user = user_db.get(user_id)
    day = int(data[3])
    post = int(data[4])
    cho = int(data[5])
    print(f"id: {post}")

    data = sch_db.get_day(day)
    date = next((d for d in data if d["id"] == post), None)
    print(f"date: {date}")
    command = f"training_day_{user["day"]}_{post + 1}"
    if "answer" in date["buttons"][cho]:
        await bot.edit_message_reply_markup(chat_id=user_id,
                                            message_id=user["message_id"],
                                            reply_markup=None)
        if "answer_button" in date["buttons"][cho]:
            keyboard = keylib.create_inline_keyboard([{"text": date["buttons"][cho]["answer_button"]["text"], "command": f"second_button_for_day_{day}_{post+1}_{date["delay"]}"}])
            message = await bot.send_message(chat_id=user_id, text=date["buttons"][cho]["answer"], reply_markup=keyboard)
            user_db.update(user_id, "message_id", message.message_id)
        else:
            message = await bot.send_message(chat_id=user_id, text=date["buttons"][cho]["answer"])
            user_db.update(user_id, "message_id", message.message_id)
            await asyncio.sleep(int(date["delay"]))
            await day_handler(bot, user_id, state, user_db, sch_db, Question, archive_helper, keylib, command)
    else:
        await asyncio.sleep(int(date["delay"]))
        await day_handler(bot=bot, user_id=user_id, state=state, user_db=user_db, sch_db=sch_db, Question=Question, archive_helper=archive_helper, keylib=keylib, data = command)



async def send_m(post, archive_helper, bot, user_id, user_db: UserDatabase):
    media_group = MediaGroupBuilder(caption=post["text"])
    if len(post["path"]) > 1:
        for path in post["path"]:
            media_group = send_media(path, archive_helper, media_group)
        message = await bot.send_media_group(chat_id=user_id, media=media_group.build())
        print(f"message: {message[0].message_id}")
        user_db.update(user_id, "message_id", message[0].message_id)
    else:
        if post["path"][0]["format"] == "image":
            message = await bot.send_photo(chat_id=user_id, photo=archive_helper.send_photo(post["path"][0]["path"]), caption=post["text"])
            user_db.update(user_id, "message_id", message.message_id)
        elif post["path"][0]["format"] == "video":
            message = await bot.send_video(chat_id=user_id, video=archive_helper.send_video(post["path"][0]["path"]), caption=post["text"])
            user_db.update(user_id, "message_id", message.message_id)

def send_media(path, archive_helper, media_group):
    if path["format"] == "image":
        pth = archive_helper.send_photo(path["path"])
        media_group.add_photo(pth)
    elif path["format"] == "video":
        pth = archive_helper.send_video(path["path"])
        media_group.add_video(pth)
    return media_group
