import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message, ErrorEvent

from .config import config
from .database.session import  init_db, get_session
from .services import DialogService
from .keyboards import keyboards
from .messages import START_MESSAGE, HELP_MESSAGE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()



@dp.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    user_id = message.from_user.id

    async with get_session() as session:
        service = DialogService(session)
        await service.reset_dialog(user_id)

    await message.answer(
        START_MESSAGE,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboards.get_main_menu_keyboard()
    )
    logger.info(f"User {user_id} started the bot")


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer(
        HELP_MESSAGE,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboards.get_main_menu_keyboard()
    )
    logger.info(f"User {message.from_user.id} requested help")


@dp.message(F.text == "🔄 Новый запрос")
async def handle_reset_button_text(message: Message):
    """Обработка нажатия на кнопку в меню"""
    await cmd_start(message)
    
    
@dp.message(F.text)
async def handle_text_message(message: Message):
    """Обработчик текстовых сообщений - основной функционал бота"""
    user_id = message.from_user.id
    user_text = message.text

    if not user_text:
        return

    logger.info(f"User {user_id} sent: {user_text[:50]}...")

    async with get_session() as session:
        try:
            # Индикатор набора текста
            await bot.send_chat_action(chat_id=message.chat.id, action="typing")

            # Делигируем бизнес логику
            service = DialogService(session)
            ai_response = await service.process_user_message(user_id, user_text)

            await message.answer(
                ai_response,
                parse_mode=ParseMode.MARKDOWN,
            )
            logger.info(f"Sent response to user {user_id}")

        except Exception as e:
            logger.error(
                f"Error handling message from user {user_id}: {e}", exc_info=True)
            await message.answer(
                "⚠️ Произошла ошибка при обработке запроса. Попробуйте ещё раз.",
            )


@dp.errors()
async def errors_handler(event: ErrorEvent):
    """Глобальный обработчик ошибок"""
    logger.error(f"Unhandled error: {event.exception}", exc_info=True)
    return True


async def on_startup():
    """Выполняется при запуске бота"""
    logger.info("Bot starting up...")
    await init_db()
    logger.info("Database initialized")

    me = await bot.get_me()
    logger.info(f"Bot @{me.username} is running")


async def on_shutdown():
    """Выполняется при остановке бота"""
    logger.info("Bot shutting down...")
    await bot.session.close()
    logger.info("Bot session closed")


async def main():
    """Точка входа в приложение"""
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("Starting polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
