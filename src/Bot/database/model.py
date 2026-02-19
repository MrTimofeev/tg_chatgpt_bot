from typing import Any
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from .session import Base


class Dialog(Base):
    """Модель диалога (сессионна информация о пользователе)"""
    __tablename__ = "dialogs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    messages = relationship("Message", back_populates="dialog", cascade="all, delete-orphan")
    
    
    def __repr__(self) -> str:
        return f"<Dialog(user_id={self.user_id})>"
    
    
class Message(Base):
    "Модель отдельного сообщения"
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dialog_id = Column(Integer, ForeignKey("dialogs.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    dialog = relationship("Dialog", back_populates="messages")
    
    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role})>"