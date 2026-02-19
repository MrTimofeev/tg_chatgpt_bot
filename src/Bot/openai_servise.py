import logging
from typing import List, Dict
from openai import AsyncOpenAI

from .config import config

logger = logging.getLogger(__name__)


class OpenAIService:
    """Сервис для работы с OpenAI-compatible API (OpenRouter, OpenAI, etc.)"""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        enable_reasoning: bool = False
    ):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.enable_reasoning = enable_reasoning
        self.system_prompt = (
            "Ты полезный, умный и вежливый ассистент. "
            "Отвечай на русском языке, если пользователь не указал иное."
        )  # TODO: вынести системый промт в другое место

    async def generate_responce(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Генерирует ответ на основе истории сообщений.
        """
        
        # Формируем полный контекст с системным промтом
        full_context = [
            {"role": "system", "content": self.system_prompt},
            *messages
        ]
        
        # Подготовка параметров запроса
        request_params = {
            "model": self.model,
            "messages": full_context,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        # Добавляем reasoning, если включено и модель поддреживает
        if self.enable_reasoning:
            request_params["extra_body"] = {"reasoning": {"enabled": True}}

        try:
            response = await self.client.chat.completions.create(**request_params)

            content = response.choices[0].message.content

            if content is None:
                logger.warning("Получен пустой ответ от OpenAI")
                return "Извините я не смог сгенерировать ответ. Попробуйте еще раз."

            return content
        except Exception as e:
            logger.error(f"Ошибка при обращении к OpenAI API: {e}")
            return self._get_error_message(e)

    def _get_error_message(self, error: Exception) -> str:
        """Возвращаем понятное сообщение об ошибке для пользователя"""

        error_str = str(error).lower()

        if "rate limit" in error_str:
            return "Cлишком много запросов. Пожалуйста, подождите немного."
        else:
            return f'Произошла ошибка, попробуйсте снова, если вы повторно увидете это сообщение обратитесь к администратору'

openai_service = OpenAIService(
    api_key=config.OPENAI_API_KEY,
    base_url=config.OPENAI_BASE_URL,
    model=config.OPENAI_MODEL,
    enable_reasoning=config.ENABLE_REASONING
)