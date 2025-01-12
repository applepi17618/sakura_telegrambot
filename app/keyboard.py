from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Начать диалог')]
], input_field_placeholder='Нажмите "Начать диалог", чтобы начать общение с Сакурой.',resize_keyboard=True)
