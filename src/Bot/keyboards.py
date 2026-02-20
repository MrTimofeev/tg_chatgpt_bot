from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

class KeyboardFactory:
    """Фабрика для создания клавиатур бота."""
    
    @staticmethod
    def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
        """
        Основное меню с кнопкой сброса контекста (через команду /start)
        Эта клавиатура появляется один рза при старте или по запросу.
        """
        
        builder = ReplyKeyboardBuilder()
        builder.button(text="🔄 Новый запрос")
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def get_empty_keyboard() -> None:
        """Возвращает None, чтобы убрать клавиатуру полностью"""
        return None
    
    
keyboards = KeyboardFactory()