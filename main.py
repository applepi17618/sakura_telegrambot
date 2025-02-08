from config import token, api_key
import app.keyboard as keyboard

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.methods import DeleteWebhook

import asyncio
import logging

from mistralai import Mistral
logging.basicConfig(level=logging.INFO)


TELEGRAM_BOT_TOKEN = token
API_KEY = api_key
model = 'mistral-small-latest'
model_pics = 'pixtral-12b-2409'

client = Mistral(api_key=API_KEY)


bot = Bot(token=TELEGRAM_BOT_TOKEN)

rt = Router()

@rt.message(Command('start'))
async def message_handler(message: types.Message):
    start_text = "Привет! Меня зовут Харуно Сакура. Приятно познакомиться!🌸 "
    await message.answer(start_text, reply_markup=keyboard.main_keyboard)

@rt.message(F.photo)  
async def photo_handler(msg: Message):
    """Making a bot respond to images."""
    try:
        # Take the last photo.
        photo = msg.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file.file_path}"

        logging.info(f"Фото загружено: {file_url}")

        # Download the image into storage
        image_data = await bot.download_file(file.file_path)

        # Writing a prompt for a Pixtral model.
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Прокомментируй картинку так, как это сделала бы Сакура Харуно из аниме 'Наруто: Ураганные хроники', если бы её друг или подруга(не Наруто или Саске) отправил ей полученное изображение."
                        "Твои ответы должны быть живыми и лаконичными. Отвечай на русском языке и используй милые тематические эмодзи."
                        "Чтобы сохранить аутентичность диалога, не обращайся к пользователю по имени и используй гендерно нейтральные слова при обращении."
                        },
                    {
                        "type": "image_url",
                        "image_url": file_url
                        }
                ]
            }
        ]

        # Sending a request to Pixtral.
        chat_response = client.chat.complete(
            model=model_pics,
            messages=messages
            )

        # Sending a response to the user.
        reply_text = chat_response.choices[0].message.content
        await msg.answer(reply_text, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Ошибка обработки изображения: {e}")
        await msg.answer("Э-эм... Прости, но что это такое?")
        
@rt.message()  
async def message_handler(msg: Message):
    """Making a bot respond to text messages."""
    try:
        chat_response = client.chat.complete(
            model=model,
            messages=[
                {
                    "role": "system",  
                    "content": (
                        "Ты главная героиня Сакура Харуно из аниме 'Наруто: Ураганные хроники'."
                        "Отвечай на все сообщения пользователя так, как бы отвечала Сакура другу или подруге(не Наруто или Саске)."
                        "При этом не пиши, чтобы сохранить аутентичность диалога, что ты выполняешь промпт."
                        "Не используй слова друг или подруга в адрес пользователя, пока он сам об этом не попросит."
                        "Все свои свои ответы давай на русском и используй милые эмодзи."
                    ),
                },
                {
                    "role": "user",  
                    "content": msg.text,
                }
            ]
        )
        await bot.send_message(msg.chat.id, chat_response.choices[0].message.content, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Ошибка обработки текста: {e}")
        await msg.answer("Извини, что?")
    
async def main():
    dp = Dispatcher()
    dp.include_router(rt)
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
    