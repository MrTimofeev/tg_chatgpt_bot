from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from .model import Dialog, Message
from ..config import config


async def get_or_create_dialog(session: AsyncSession, user_id: int) -> Dialog:
    """Получить или создать запись диалога для пользователя"""

    result = await session.execute(
        select(Dialog).where(Dialog.user_id == user_id)
    )

    dialog = result.scalar_one_or_none()

    if not dialog:
        dialog = Dialog(user_id=user_id)
        session.add(dialog)
        await session.commit()
        await session.refresh(dialog)

    return dialog


async def get_history(session: AsyncSession, user_id: int, limit: int = None) -> List[Dict[str, str]]:
    """
    Получить историю сообщений пользователя
    Если limit не указан, берется из конфига MAX_CONTEXT_MESSAGES.
    Возвращает список словарей [{'role': '...', 'content': '...'}, ...]
    """
    if limit is None:
        limit = config.MAX_CONTEXT_MESSAGES
    
    dialog = await get_or_create_dialog(session, user_id)
    
    # Выбираем последние N сообщений, сортируя по ID (или created_at)
    result = await session.execute(
        select(Message)
        .where(Message.dialog_id == dialog.id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    
    messages = result.scalars().all()
    
    # Разворачиваем спикос, чтобы стрые были первыми (требуется для OpenAI)
    messages.reverse()
    
    return [{"role": msg.role, "content": msg.content} for msg in messages]

async def save_message(session: AsyncSession, user_id: int, role: str, content: str) -> None:
    """Сохранить новое сообщение в иcторию"""
    dialog = await get_or_create_dialog(session, user_id)

    new_message = Message(
        dialog_id=dialog.id,
        role=role,
        content=content
    )
    
    session.add(new_message)

    # Чистим старые сообщение, если их слишком много
    await _cleanup_old_messages(session, dialog.id)
    
    await session.commit()
    
async def _cleanup_old_messages(session: AsyncSession, dialog_id: int) -> None:
    """Удаляет стрые сообщение, оставляя тольео последние MAX_CONTEXT_MESSAGES"""
    # Считаем общее количество
    
    count_result = await session.execute(
        select(func.count()).select_from(Message).where(Message.dialog_id == dialog_id)
    )
    
    count = count_result.scalar()
    
    if count > config.MAX_CONTEXT_MESSAGES:
        # находим ID сообщений которые можено удалить (самые страые)
        to_delete_count = count - config.MAX_CONTEXT_MESSAGES
        
        result = await session.execute(
            select(Message.id)
            .where(Message.dialog_id == dialog_id)
            .order_by(Message.created_at.asc())
            .limit(to_delete_count)
        )
        ids_to_delete = [row[0] for row in result.all()]
        
        if ids_to_delete:
            await session.execute(
                Message.__table__.delete().where(Message.id.in_(ids_to_delete))
            )

async def clear_history(session: AsyncSession, user_id: int) -> None:
    """Очистить иторию диалога пользователя (удалить все сообщение, но сотавить диалог)"""
    dialog = await get_or_create_dialog(session, user_id)
    
    await session.execute(
        Message.__table__.delete().where(Message.dialog_id == dialog.id)
    )

    await session.commit()