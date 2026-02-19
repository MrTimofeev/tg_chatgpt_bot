import logging
from typing import List, Dict
from openai import AsyncOpenAI

from ..config import config
from ..prompts import SYSTEM_PROMPT


logger = logging.getLogger(__name__)


class OpenAIService:
    """Низкоуровневый серсив для взаимодействия с LLM API"""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
    ):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Отправляет запрос к API и возвращает тектовый ответ
        """

        # Формируем полный контекст с системным промтом
        full_context = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=full_context,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            if not response.choices or not response.choices[0].message.content:
                logger.warning("Получен пустой ответ от OpenAI")
                return "Извините, я не смог сненерировать ответ. Попробуйте еще раз."

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Ошибка при обращении к OpenAI API: {e}", exc_info=True)
            return self._get_error_message(e)

    def _get_error_message(self, error: Exception) -> str:
        """Возвращаем понятное сообщение об ошибке для пользователя"""

        error_str = str(error).lower()

        if "rate limit" in error_str:
            return "⏳ Слишком много запросов. Пожалуйста, подождите немного."
        elif "authentication" in error_str or "api key" in error_str:
            return "🔑 Ошибка авторизации. Проверьте настройки API ключа."
        else:
            return (
                "⚠️ Произошла ошибка. Попробуйте снова. "
                "Если проблема повторится, обратитесь к администратору."
            )


openai_service = OpenAIService(
    api_key=config.OPENAI_API_KEY,
    base_url=config.OPENAI_BASE_URL,
    model=config.OPENAI_MODEL,
)
