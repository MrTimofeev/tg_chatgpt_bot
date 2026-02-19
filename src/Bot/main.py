import asyncio
import logging
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message, ErrorEvent
from sqlalchemy.ext.asyncio import AsyncSession

from .config import config
from .database import get_session, init_db, save_message, get_history, clear_history
from .openai_servise import openai_service
from .keyboards import keyboards
from .database.session import async_session_maker


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

@asynccontextmanager
async def get_db_session():
    """Контекстный менеджер для безопасной работы с сессией БД"""
    session = async_session_maker()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        await session.close()
            
@dp.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    
    # Сбрасываем историю при старте
    async with get_db_session() as session:
        await clear_history(session, user_id)
        
    text = (
         "👋 *Привет! Я AI-ассистент на базе ChatGPT.*\n\n"
        "Я могу:\n"
        "• Отвечать на вопросы\n"
        "• Помогать с текстами и идеями\n"
        "• Поддерживать контекст диалога\n\n"
        "Просто напиши мне любое сообщение, и я постараюсь помочь! 🚀\n\n"
        "Используй /help для подробной справки."
    )
    
    await message.answer(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboards.get_reset_inline_keyboard()
    )
    logger.info(f"User {user_id} start the bot")
    
@dp.message(Command("help"))
async def cmd_hepl(message: Message):
    """Обработчк команды /help"""
    
    text = (
        "📚 *Справка по боту*\n\n"
        "*Команды:*\n"
        "/start — Запустить бота и очистить историю\n"
        "/help — Показать это сообщение\n\n"
        "*Функции:*\n"
        "• Отправь любой текст — получи ответ от AI\n"
        "• Бот помнит контекст предыдущих сообщений\n"
        "• Кнопка «🔄 Новый запрос» очистит контекст\n\n"
        "*Советы:*\n"
        "• Задавай конкретные вопросы для лучших ответов\n"
        "• Используй «Новый запрос» для смены темы"
    )
    
    await message.answer(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboards.get_reset_inline_keyboard()
    )
    logger.info(f"User {message.from_user.id} requested help")
    
@dp.callback_query(F.data == "reset_context")
async def porcess_reset_callback(callback: CallbackQuery):
    """Обработчк нажатия кнопки <Новый зарос>"""
    
    user_id = callback.from_user.id
    
    async with get_db_session() as session:
        await clear_history(session, user_id)
        
    await callback.answer("🗑️ Контекст очищен!", show_alert=False)
    
    await callback.message.edit_reply_markup(
        reply_markup=keyboards.get_reset_inline_keyboard()
    )
    
    await callback.message.answer(
        "✅ История диалога сброшена. Можешь начать новый разговор!",
        reply_markup=keyboards.get_reset_inline_keyboard()
    )
    
    logger.info(f"User {user_id} reset conversation context")
    
@dp.message(F.text)
async def handle_text_message(message: Message):
    """Обработчик текстовых сообщений - основной функционал бота"""
    user_id = message.from_user.id
    user_text = message.text.split()
    
    if not user_text:
        return
    
    logger.info(f"User {user_id} sent: {user_text[:50]}...")
    
    async with get_db_session() as session:
        try:
            # 1. Сохряняем сообщение пользователя в БД
            await save_message(session, user_id, "user", user_text)
            
            # 2. Получаем актуальную иторию диалога
            history = await get_history(session, user_id)
            
            # 3. Показываем индикатор набора текста 
            await bot.send_chat_action(chat_id=message.chat.id, action="typing")
            
            # 4. Запрос к OpenAI сервису.
            ai_response = await openai_service.generate_responce(history)
            
            # 5. Сохраняем ответ ассистента в БД
            await save_message(session, user_id, "assistant", ai_response)
            
            # 6. Отправляем ответ пользователю
            
            await message.answer(
                ai_response,
                reply_markup=keyboards.get_reset_inline_keyboard()
            )
            
            logger.info(f"Sent response to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error handling message from user {user_id}: {e}", exc_info=True)
            await message.answer(
                "⚠️ Произошла ошибка при обработке запроса. Попробуйте ещё раз.",
                reply_markup=keyboards.get_reset_inline_keyboard()
            )
            
@dp.errors()
async def errors_handler(event: ErrorEvent):
    """Глобавльный обработчик ошибок"""
    exception = event.exception
    logger.error(f"Unhandled error: {exception}", exc_info=True)
    
    return True

async def on_statup():
    """Выпоняется при запуске бота"""
    logger.info("Bot starting up...")
    await init_db()
    logger.info("Database initialized")
    
    me = await bot.get_me()
    logger.info(f"Bot @{me.username} is running")
    
async def on_shutdown():
    """Выполняется при остановке бота"""
    logger.info("Bot shutting dowm...")
    await bot.session.close()
    logger.info("Bot session closed")


async def main():
    """Точка входа в приложение"""

    dp.startup.register(on_statup)
    dp.shutdown.register(on_shutdown)
    
    logger.info("Statring polling...")
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Bot crashed: {e}", exc_info=True)