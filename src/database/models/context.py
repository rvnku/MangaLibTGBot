from __future__ import annotations

from datetime import datetime, UTC
from typing import Optional
from typing import TYPE_CHECKING

from sqlalchemy import SmallInteger, BigInteger, JSON, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.database.models.base import Base
from src.database.states import State

if TYPE_CHECKING:
    from src.database.models.user import UserModel


class ContextModel(Base):
    __tablename__ = 'context'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram_id'))
    chat_id: Mapped[int] = mapped_column(BigInteger)
    head_message_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    body_message_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    site_id: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    state: Mapped[Optional[Enum[State]]] = mapped_column(Enum(State), nullable=True)
    data: Mapped[JSON] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC), nullable=True)

    user: Mapped[UserModel] = relationship('UserModel', back_populates='contexts')
