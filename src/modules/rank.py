"""
Módulo de sistema de rank
"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

from src.database.db import db
from src.utils.responses import responses


async def track_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Rastreia mensagens para o sistema de rank"""
    if not update.message or not update.effective_chat or not update.effective_user:
        return
    
    # Não conta comandos
    if update.message.text and update.message.text.startswith('/'):
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    # Salva usuário e incrementa contador
    async for session in db.get_session():
        await db.get_or_create_user(
            session, 
            user.id, 
            user.username, 
            user.first_name,
            user.last_name
        )
        await db.get_or_create_group(
            session,
            chat.id,
            chat.title or "Unknown"
        )
        await db.increment_message_count(session, user.id, chat.id)
        break


async def rank_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /rank - Mostra posição no ranking"""
    if not update.message or not update.effective_chat or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    async for session in db.get_session():
        position, count = await db.get_user_rank(session, user_id, chat_id)
        
        if position == 0:
            await update.message.reply_text(responses.RANK_NOT_FOUND)
        else:
            await update.message.reply_text(
                responses.RANK_MESSAGE.format(position=position, count=count)
            )
        break


def register_rank_handlers(application) -> None:
    """Registra handlers de rank"""
    application.add_handler(CommandHandler("rank", rank_command))
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            track_messages
        ),
        group=1
    )
