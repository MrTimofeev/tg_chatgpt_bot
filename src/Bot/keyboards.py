from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

class KeyboardFactory:
    """Фабрика для создания клавиатур бота."""
    
    @staticmethod
    def get_reset_inline_keyboard() -> InlineKeyboardMarkup:
        """
        Инлайн-клавиатура с кнопкой сброса контекста.
        Отображается под каждым сообщением бота.
        """
        builder = InlineKeyboardBuilder()
        builder.button(
            text="🔄 Новый запрос",
            callback_data="reset_context"
        )
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def get_start_reply_keyboard() -> ReplyKeyboardMarkup:
        """
        Reply-клавиатура для команды /start
        """
        builder = ReplyKeyboardBuilder()
        builder.button(text="🔄 Новый запрос")
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def get_empty_inline_keyboard() -> InlineKeyboardMarkup:
        """Пустая клавиатура - чтобы убрать кнопки"""
        return InlineKeyboardMarkup(inline_keyboard=[])
    
keyboards = KeyboardFactory()