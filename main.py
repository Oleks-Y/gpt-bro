import os
import openai
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils import executor

# Set up API keys
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
TELEGRAM_API_KEY = os.environ["TELEGRAM_API_KEY"]

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_API_KEY)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware(logger=logging.getLogger()))

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY
openai.log = "info"

# Initialize chat histories
chat_histories = {}


async def on_start(message: types.Message):
    await message.reply("Welcome! Send a message followed by the /prompt command to get a response.")


async def store_message(message: types.Message):
    chat_id = message.chat.id
    if chat_id not in chat_histories:
        chat_histories[chat_id] = []

    chat_histories[chat_id].append(message.text)

    # Keep only the last 10 messages
    chat_histories[chat_id] = chat_histories[chat_id][-10:]

    print("stored message:", message.text)


async def prompt(message: types.Message):
    if not message.text.startswith("/prompt"):
        return

    prompt_text = message.text[8:].strip()

    if not prompt_text:
        await message.reply("Please provide a prompt.")
        return

    chat_id = message.chat.id
    messages = [{"role": "user", "content": msg}
                for msg in chat_histories.get(chat_id, [])]

    messages.append({"role": "user", "content": prompt_text})

    print("sending prompt:", messages)

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    answer = completion.choices[0].message["content"]
    message_reply = await message.reply(answer, parse_mode=ParseMode.MARKDOWN)

    await store_message(message)
    await store_message(message_reply)


# Register message handlers
dp.register_message_handler(on_start, commands=["start", "help"])
dp.register_message_handler(prompt, commands=["prompt"])
dp.register_message_handler(store_message)


if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
