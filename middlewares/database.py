from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class DatabaseMiddleware(BaseMiddleware):
    """Middleware to handle database sessions"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Execute handler with database session cleanup
        """
        try:
            # Execute handler
            result = await handler(event, data)
            return result
        finally:
            # Clean up database sessions
            from database import close_session
            close_session()