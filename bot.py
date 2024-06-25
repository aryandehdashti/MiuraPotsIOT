import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher

TOKEN = ""
CHAT_ID = ""

bot = Bot(token=TOKEN)

async def send_message(pot_name):
    message = f'''خشک است {pot_name} گلدان '''
    try:
        message = await bot.send_message(CHAT_ID, message)
    except Exception as e:
        logging.error(e)


async def main() -> None:
    dp = Dispatcher()
    await dp.start_polling(bot)
    
if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
