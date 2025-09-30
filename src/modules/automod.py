"""
Módulo de AutoMod - Filtros automáticos de links, spam e conteúdo
"""
import re
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from telegram.error import TelegramError

from src.utils.permissions import bot_can_delete
from src.utils.responses import responses
from src.database.db import db
from sqlalchemy import select
from src.database.models import Group


async def check_automod(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Verifica mensagens para AutoMod"""
    if not update.message or not update.effective_chat or not update.effective_user:
        return
    
    # Não modera admins
    try:
        member = await context.bot.get_chat_member(
            update.effective_chat.id,
            update.effective_user.id
        )
        if member.status in ["administrator", "creator"]:
            return
    except Exception:
        pass
    
    # Verifica configurações do grupo
    async for session in db.get_session():
        result = await session.execute(
            select(Group).where(Group.id == update.effective_chat.id)
        )
        group = result.scalar_one_or_none()
        
        if not group or not group.automod_enabled:
            return
        
        # Filtro de links
        if group.filter_links and update.message.text:
            if check_links(update.message.text):
                if await bot_can_delete(update, context):
                    try:
                        await update.message.delete()
                        warning = await update.message.reply_text(responses.LINK_DETECTED)
                        await context.application.create_task(
                            delete_after_delay(warning, 5)
                        )
                    except TelegramError:
                        pass
                return
        
        # Filtro de spam (mensagens repetidas rapidamente)
        if group.filter_spam:
            # Implementação básica - pode ser expandida
            if update.message.text and len(update.message.text) > 500:
                if await bot_can_delete(update, context):
                    try:
                        await update.message.delete()
                        warning = await update.message.reply_text(responses.SPAM_DETECTED)
                        await context.application.create_task(
                            delete_after_delay(warning, 5)
                        )
                    except TelegramError:
                        pass
        
        break


async def delete_after_delay(message, delay: int) -> None:
    """Deleta mensagem após um delay"""
    import asyncio
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass


def check_links(text: str) -> bool:
    """Verifica se há links no texto"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return bool(re.search(url_pattern, text))


def register_automod_handlers(application) -> None:
    """Registra handlers de AutoMod"""
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            check_automod
        ),
        group=0
    )
