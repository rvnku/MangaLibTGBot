from __future__ import annotations

from datetime import datetime, UTC
from typing import List, Optional
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.database.models.base import Base
if TYPE_CHECKING:
    from src.database.models.context import ContextModel


class UserModel(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id: Mapped[int] = mapped_column(Integer, nullable=True)
    token: Mapped[Optional[str]] = mapped_column(String(2048), default=None, nullable=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC), nullable=True)
    login_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=None, nullable=True)
    logout_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=None, nullable=True)

    contexts: Mapped[List[ContextModel]] = relationship('ContextModel', back_populates='user')
