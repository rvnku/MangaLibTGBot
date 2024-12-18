from __future__ import annotations
from datetime import datetime, UTC
from sqlalchemy.orm import joinedload
from src.database import async_session
from src.database.models import ContextModel, UserModel
from src.database.states import State
from sqlalchemy import update, select, or_, and_
from typing import Dict, Any, Optional


class Context:
    id: int = None
    telegram_id: int = ...
    chat_id: int = ...
    head_message_id: Optional[int] = None
    body_message_id: Optional[int] = None
    site_id: int = ...
    state: Optional[State] = None
    data: Dict[str, Any] = None
    user_id: Optional[int] = None
    user_token: Optional[str] = None

    def __init__(
        self,
        id: int = ...,
        telegram_id: Optional[int] = ...,
        chat_id: Optional[int] = ...,
        head_message_id: Optional[int] = None,
        body_message_id: Optional[int] = None,
        site_id: Optional[int] = ...,
        state: Optional[State] = None,
        data: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = ...,
        user_token: Optional[str] = ...,
    ) -> None:
        if not isinstance(id, type(...)):
            self.id = id
        if not isinstance(telegram_id, type(...)):
            self.telegram_id = telegram_id
        else:
            raise ValueError('The user_id field is required')
        if not isinstance(chat_id, type(...)):
            self.chat_id = chat_id
        else:
            raise ValueError('The chat_id field is required')
        self.head_message_id = head_message_id
        self.body_message_id = body_message_id
        if not isinstance(site_id, type(...)):
            self.site_id = site_id
        else:
            raise ValueError('The site_id field is required')
        self.state = state
        self.data = data or {}
        if not isinstance(user_id, type(...)):
            self.user_id = user_id
        if not isinstance(user_token, type(...)):
            self.user_token = user_token

    async def save(self) -> None:
        async with async_session() as session:
            if self.id:
                await session.execute(
                    update(ContextModel)
                    .where(or_(ContextModel.id == self.id))
                    .values(
                        telegram_id=self.telegram_id,
                        chat_id=self.chat_id,
                        head_message_id=self.head_message_id,
                        body_message_id=self.body_message_id,
                        state=self.state,
                        data=self.data,
                        updated_at=datetime.now(UTC)
                    )
                )
            else:
                context = ContextModel(
                    telegram_id=self.telegram_id,
                    chat_id=self.chat_id,
                    head_message_id=self.head_message_id,
                    body_message_id=self.body_message_id,
                    site_id=self.site_id,
                    state=self.state,
                    data=self.data
                )
                self.id = context.id
                session.add(context)
            await session.commit()

    async def load(self) -> None:
        async with async_session() as session:
            if self.id:
                result = await session.execute(
                    select(ContextModel)
                    .options(joinedload(ContextModel.user))
                    .where(or_(ContextModel.id == self.id))
                )
                context = result.scalar_one_or_none()
                self.telegram_id = context.telegram_id
                self.chat_id = context.chat_id
                self.head_message_id = context.head_message_id
                self.body_message_id = context.body_message_id
                self.state = context.state
                self.data = context.data
                self.user_id = context.user.id
                self.user_token = context.user.token
            else:
                result = await session.execute(
                    select(UserModel)
                    .where(or_(UserModel.telegram_id == self.telegram_id))
                )
                user = result.scalar_one_or_none()
                self.user_id = user.id
                self.user_token = user.token

    @staticmethod
    async def get_context_from(message_id: int) -> Optional[Context]:
        async with async_session() as session:
            result = await session.execute(
                select(ContextModel)
                .options(joinedload(ContextModel.user))
                .where(or_(ContextModel.head_message_id == message_id, ContextModel.body_message_id == message_id))
            )
            if context := result.scalar_one_or_none():
                return Context(
                    id=context.id,
                    telegram_id=context.telegram_id,
                    chat_id=context.chat_id,
                    head_message_id=context.head_message_id,
                    body_message_id=context.body_message_id,
                    site_id=context.site_id,
                    state=context.state,
                    data=context.data,
                    user_id=context.user.id,
                    user_token=context.user.token
                )
            return

    @staticmethod
    async def get_last_from(telegram_id: int, chat_id: int) -> Optional[Context]:
        async with async_session() as session:
            result = await session.execute(
                select(ContextModel)
                .options(joinedload(ContextModel.user))
                .where(and_(
                    ContextModel.telegram_id == telegram_id,
                    ContextModel.chat_id == chat_id
                ))
                .order_by(ContextModel.created_at.desc())
                .limit(1)
            )
            if context := result.scalar_one_or_none():
                return Context(
                    id=context.id,
                    telegram_id=context.telegram_id,
                    chat_id=context.chat_id,
                    head_message_id=context.head_message_id,
                    body_message_id=context.body_message_id,
                    site_id=context.site_id,
                    state=context.state,
                    data=context.data,
                    user_id=context.user.id,
                    user_token=context.user.token
                )
            return
