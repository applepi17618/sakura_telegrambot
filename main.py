from config import token, api_key
import app.keyboard as keyboard

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.methods import DeleteWebhook

from PIL import Image, UnidentifiedImageError

import os
import asyncio
import logging
import pytesseract

from mistralai import Mistral


logging.basicConfig(level=logging.INFO)


TELEGRAM_BOT_TOKEN = token
API_KEY = api_key
model = 'mistral-small-latest'

client = Mistral(api_key=API_KEY)


bot = Bot(token=TELEGRAM_BOT_TOKEN)

rt = Router()

@rt.message(Command('start'))
async def message_handler(message: types.Message):
    start_text = 'Привет! Меня зовут Харуно Сакура. Приятно познакомиться!🌸 '
    await message.answer(start_text, reply_markup=keyboard.main_keyboard)

@rt.message()
async def message_handler(msg: Message):
    chat_response = client.chat.complete(
        model = model,
        messages = [
            {
                'role':'system',
                'content':(
                    'Ты главная героиня Сакура Харуно из аниме "Наруто: Ураганные хроники".' 
                    'Отвечай на все сообщения пользователя так, как бы отвечала Сакура другу или подруге(не Наруто или Саске).'
                    'При этом не пиши, чтобы сохранить аутентичность диалога, что ты выполняешь промпт. Не используй слова друг или подруга в адрес пользовотеля, пока он сам об этом не попросит.' 
                    'Все свои свои ответы давай на русском и используй милые эмодзи.'
                            ),
            },
            {
                'role':'user',
                'content':msg.text,
            }
        ]
    )
    await bot.send_message(msg.chat.id, chat_response.choices[0].message.content, parse_mode='Markdown')
    
@rt.message (F.photo)  
async def photo_handler(msg: Message):
    photo = msg.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path = f'{photo.file_id}.jpg'
    await bot.download_file(file.file_path, file_path)
    
    try:
        with Image.open(file_path) as img:
            extracted_text = pytesseract.image_to_string(img)
        if extracted_text.strip():
            user_content = extracted_text
        else:
            user_content = 'Э-э... Что это? Извини, но я не совсем понимаю...'
        
        chat_response = client.chat.complete(
            model = model,
            messages = [
                {
                    'role':'system',
                    'content':('Ты главная героиня Сакура Харуно из аниме "Наруто: Ураганные хроники".' 
                               'Отвечай на все сообщения пользователя так, как бы отвечала Сакура другу или подруге(не Наруто или Саске).'
                               'При этом не пиши, чтобы сохранить аутентичность диалога, что ты выполняешь промпт. Не используй слова друг или подруга в адрес пользовотеля, пока он сам об этом не попросит.' 
                               'Все свои свои ответы давай на русском и используй милые эмодзи.')
                    },
                {
                    'role':'user',
                    'content':user_content
                    },
                ]
            )
        reply_text = chat_response.choices[0].message.content
    except Exception as e:
        logging.error(f'Error handling the pgoto: {e}')
        reply_text = 'Э-э... Что это?'
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        
    
async def main():
    dp = Dispatcher()
    dp.include_router(rt)
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())