import json
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .model import Dialog
from ..config import config


async def get_or_create_dialog(session: AsyncSession, user_id: int) -> Dialog:
    """Получить или создать запись диалога для пользователя"""

    result = await session.execute(
        select(Dialog).where(Dialog.user_id == user_id)
    )

    dialog = result.scalar_one_or_none()

    if not dialog:
        dialog = Dialog(user_id=user_id, messages="[]")
        session.add(dialog)
        await session.commit()
        await session.refresh(dialog)

    return dialog


async def get_history(session: AsyncSession, user_id: int) -> List[Dict[str, str]]:
    """Получить историю сообщений пользователя"""

    dialog = await get_or_create_dialog(session, user_id)
    return json.loads(dialog.messages)


async def save_message(session: AsyncSession, user_id: int, role: str, content: str) -> None:
    """Сохранить новое сообщение в иторию"""

    dialog = await get_or_create_dialog(session, user_id)

    messages = json.loads(dialog.messages)

    messages.append({"role": role, "content": content})

    # Ограничиваем контекст
    if len(messages) > config.MAX_CONTEXT_MESSAGES:
        messages = messages[-config.MAX_CONTEXT_MESSAGES:]

    dialog.messages = json.dumps(messages, ensure_ascii=False)

    await session.commit()
    await session.refresh(dialog)


async def clear_history(session: AsyncSession, user_id: int) -> None:
    """Очистить иторию диалога пользователя"""
    result = await session.execute(
        select(Dialog).where(Dialog.user_id == user_id)
    )

    dialog = result.scalar_one_or_none()

    if dialog:
        dialog.messages = "[]"
        await session.commit()
