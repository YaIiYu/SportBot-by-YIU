from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, InlineKeyboardMarkup, InlineKeyboardButton


class Keyboard_Library:

    def set_training_keyboard(self,day) -> ReplyKeyboardMarkup:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=f"День {day}")],
            ],
            resize_keyboard=True, one_time_keyboard=True
        )
        return keyboard

    def create_inline_keyboard(self, buttons=None):
        if buttons is None:
            buttons = [{"text": "text", "command": "command"}]
        return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button["text"], callback_data=button["command"])] for button in buttons
    ])

