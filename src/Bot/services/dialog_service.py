import logging

from sqlalchemy.ext.asyncio import AsyncSession

from .openai_service import openai_service
from ..database.crud import (
    get_history,
    save_message,
    clear_history as db_clear_history
)

logger = logging.getLogger(__name__)


class DialogService:
    """
    Бизнес-логика управления диалогами.
    Координирует сохранение истории, получение контекста и генерацию ответов.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def process_user_message(self, user_id: int, user_text: str) -> str:
        """
        Полный цикл обработки сообщения пользователя:
        1. Сохранить вопрос пользователя.
        2. Получить историю.
        3. Запросить ответ у AI.
        4. Сохранить ответ AI.
        5. Вернуть ответ.
        """
        # 1. Сохраняем входное сообщение
        await save_message(self.session, user_id, role="user", content=user_text)
        
        # 2. Получаем актуальную историю (с учетом лимита контекста внутри CRUD)
        history = await get_history(self.session, user_id)
        
        # 3. Генерируем ответ через AI сервис
        ai_response = await openai_service.generate_response(history)
        
        # 4. Сохраняем ответ ассистента
        await save_message(self.session, user_id, role="assistant", content=ai_response)
        
        return ai_response

    async def reset_dialog(self, user_id: int) -> None:
        """Очищает историю диалога для пользователя."""
        await db_clear_history(self.session, user_id)
        logger.info(f"Диалог для пользователя {user_id} сброшен.")