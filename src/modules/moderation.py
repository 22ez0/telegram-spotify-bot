"""
Módulo de moderação - Ban, Mute, Kick, Unban, Nuke, Purge
"""
import asyncio
import re
from datetime import datetime, timedelta
from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, CommandHandler
from telegram.error import TelegramError

from src.utils.permissions import is_admin, bot_can_restrict, bot_can_delete, get_user_from_message
from src.utils.responses import responses
from src.database.db import db


def parse_duration(duration_str: str) -> timedelta | None:
    """Parse duração como '5 minutos', '1 hora', '30 segundos'"""
    pattern = r'(\d+)\s*(segundo|segundos|minuto|minutos|hora|horas|dia|dias)s?'
    match = re.match(pattern, duration_str.lower())
    
    if not match:
        return None
    
    amount = int(match.group(1))
    unit = match.group(2)
    
    if 'segundo' in unit:
        return timedelta(seconds=amount)
    elif 'minuto' in unit:
        return timedelta(minutes=amount)
    elif 'hora' in unit:
        return timedelta(hours=amount)
    elif 'dia' in unit:
        return timedelta(days=amount)
    
    return None


async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /ban - Bane usuário permanentemente"""
    if not update.message or not update.effective_chat:
        return
    
    # Verifica permissões
    if not await is_admin(update, context):
        await update.message.reply_text(responses.NO_PERMISSION)
        return
    
    if not await bot_can_restrict(update, context):
        await update.message.reply_text(responses.BOT_NO_PERMISSION)
        return
    
    # Obtém usuário
    user_id, user_mention = get_user_from_message(update)
    
    if not user_id and not user_mention:
        await update.message.reply_text(
            responses.INVALID_SYNTAX.format(syntax="/ban @usuario {motivo} ou responda a uma mensagem com /ban {motivo}")
        )
        return
    
    # Obtém motivo
    reason = " ".join(context.args) if context.args else "Não especificado"
    
    try:
        if user_id:
            await context.bot.ban_chat_member(update.effective_chat.id, user_id)
            
            # Log no banco
            async for session in db.get_session():
                await db.log_moderation(
                    session, 
                    update.effective_chat.id, 
                    update.effective_user.id,
                    user_id,
                    "ban",
                    reason
                )
                break
            
            await update.message.reply_text(
                responses.BAN_SUCCESS.format(user=user_mention or f"ID:{user_id}")
            )
        else:
            await update.message.reply_text(responses.USER_NOT_FOUND)
    except TelegramError as e:
        await update.message.reply_text(f"{responses.OPERATION_FAILED}\nErro: {str(e)}")


async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /kick - Remove usuário do grupo"""
    if not update.message or not update.effective_chat:
        return
    
    if not await is_admin(update, context):
        await update.message.reply_text(responses.NO_PERMISSION)
        return
    
    if not await bot_can_restrict(update, context):
        await update.message.reply_text(responses.BOT_NO_PERMISSION)
        return
    
    user_id, user_mention = get_user_from_message(update)
    
    if not user_id and not user_mention:
        await update.message.reply_text(
            responses.INVALID_SYNTAX.format(syntax="/kick @usuario ou responda a uma mensagem com /kick")
        )
        return
    
    try:
        if user_id:
            await context.bot.ban_chat_member(update.effective_chat.id, user_id)
            await context.bot.unban_chat_member(update.effective_chat.id, user_id)
            
            async for session in db.get_session():
                await db.log_moderation(
                    session, 
                    update.effective_chat.id, 
                    update.effective_user.id,
                    user_id,
                    "kick"
                )
                break
            
            await update.message.reply_text(
                responses.KICK_SUCCESS.format(user=user_mention or f"ID:{user_id}")
            )
        else:
            await update.message.reply_text(responses.USER_NOT_FOUND)
    except TelegramError as e:
        await update.message.reply_text(f"{responses.OPERATION_FAILED}\nErro: {str(e)}")


async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /mute - Silencia usuário"""
    if not update.message or not update.effective_chat:
        return
    
    if not await is_admin(update, context):
        await update.message.reply_text(responses.NO_PERMISSION)
        return
    
    if not await bot_can_restrict(update, context):
        await update.message.reply_text(responses.BOT_NO_PERMISSION)
        return
    
    user_id, user_mention = get_user_from_message(update)
    
    if not user_id and not user_mention:
        await update.message.reply_text(
            responses.INVALID_SYNTAX.format(syntax="/mute @usuario {tempo} ou responda a uma mensagem com /mute {tempo}")
        )
        return
    
    # Parse duração se fornecida
    duration = None
    duration_str = " ".join(context.args) if context.args else None
    
    if duration_str:
        duration = parse_duration(duration_str)
        if not duration:
            await update.message.reply_text(responses.INVALID_DURATION)
            return
    
    permissions = ChatPermissions(can_send_messages=False)
    
    try:
        if user_id:
            until_date = datetime.now() + duration if duration else None
            await context.bot.restrict_chat_member(
                update.effective_chat.id, 
                user_id, 
                permissions,
                until_date=until_date
            )
            
            async for session in db.get_session():
                await db.log_moderation(
                    session, 
                    update.effective_chat.id, 
                    update.effective_user.id,
                    user_id,
                    "mute",
                    duration=duration_str
                )
                break
            
            if duration:
                await update.message.reply_text(
                    responses.MUTE_TIMED_SUCCESS.format(
                        user=user_mention or f"ID:{user_id}",
                        duration=duration_str
                    )
                )
            else:
                await update.message.reply_text(
                    responses.MUTE_SUCCESS.format(user=user_mention or f"ID:{user_id}")
                )
        else:
            await update.message.reply_text(responses.USER_NOT_FOUND)
    except TelegramError as e:
        await update.message.reply_text(f"{responses.OPERATION_FAILED}\nErro: {str(e)}")


async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /unmute - Remove silenciamento"""
    if not update.message or not update.effective_chat:
        return
    
    if not await is_admin(update, context):
        await update.message.reply_text(responses.NO_PERMISSION)
        return
    
    if not await bot_can_restrict(update, context):
        await update.message.reply_text(responses.BOT_NO_PERMISSION)
        return
    
    user_id, user_mention = get_user_from_message(update)
    
    if not user_id and not user_mention:
        await update.message.reply_text(
            responses.INVALID_SYNTAX.format(syntax="/unmute @usuario ou responda a uma mensagem com /unmute")
        )
        return
    
    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_change_info=False,
        can_invite_users=True,
        can_pin_messages=False
    )
    
    try:
        if user_id:
            await context.bot.restrict_chat_member(
                update.effective_chat.id, 
                user_id, 
                permissions
            )
            
            await update.message.reply_text(
                responses.UNMUTE_SUCCESS.format(user=user_mention or f"ID:{user_id}")
            )
        else:
            await update.message.reply_text(responses.USER_NOT_FOUND)
    except TelegramError as e:
        await update.message.reply_text(f"{responses.OPERATION_FAILED}\nErro: {str(e)}")


async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /unban - Remove banimento"""
    if not update.message or not update.effective_chat:
        return
    
    if not await is_admin(update, context):
        await update.message.reply_text(responses.NO_PERMISSION)
        return
    
    if not await bot_can_restrict(update, context):
        await update.message.reply_text(responses.BOT_NO_PERMISSION)
        return
    
    user_id, user_mention = get_user_from_message(update)
    
    if not user_id and not user_mention:
        await update.message.reply_text(
            responses.INVALID_SYNTAX.format(syntax="/unban @usuario")
        )
        return
    
    try:
        if user_id:
            await context.bot.unban_chat_member(update.effective_chat.id, user_id, only_if_banned=True)
            
            await update.message.reply_text(
                responses.UNBAN_SUCCESS.format(user=user_mention or f"ID:{user_id}")
            )
        else:
            await update.message.reply_text(responses.USER_NOT_FOUND)
    except TelegramError as e:
        await update.message.reply_text(f"{responses.OPERATION_FAILED}\nErro: {str(e)}")


async def nuke_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /nuke - Deleta TODAS as mensagens do grupo"""
    if not update.message or not update.effective_chat:
        return
    
    if not await is_admin(update, context):
        await update.message.reply_text(responses.NO_PERMISSION)
        return
    
    if not await bot_can_delete(update, context):
        await update.message.reply_text(responses.BOT_NO_PERMISSION)
        return
    
    progress_msg = await update.message.reply_text(responses.NUKE_IN_PROGRESS)
    
    deleted_count = 0
    batch_size = 100
    
    try:
        # Obtém o ID da mensagem atual
        current_message_id = update.message.message_id
        
        # Tenta deletar mensagens em batches, indo de trás para frente
        for offset in range(0, 10000, batch_size):
            message_ids = list(range(current_message_id - offset - batch_size, current_message_id - offset))
            
            if not message_ids or message_ids[0] < 1:
                break
            
            try:
                # Deleta em batch
                for msg_id in message_ids:
                    try:
                        await context.bot.delete_message(update.effective_chat.id, msg_id)
                        deleted_count += 1
                    except TelegramError:
                        pass
                
                await asyncio.sleep(1)
            except Exception:
                break
        
        await progress_msg.edit_text(responses.NUKE_SUCCESS)
        await asyncio.sleep(3)
        await progress_msg.delete()
        
    except Exception as e:
        await progress_msg.edit_text(f"{responses.OPERATION_FAILED}\nErro: {str(e)}")


async def purge_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /purge - Remove mensagens específicas de um usuário"""
    if not update.message or not update.effective_chat:
        return
    
    if not await is_admin(update, context):
        await update.message.reply_text(responses.NO_PERMISSION)
        return
    
    if not await bot_can_delete(update, context):
        await update.message.reply_text(responses.BOT_NO_PERMISSION)
        return
    
    user_id, user_mention = get_user_from_message(update)
    
    # Obtém quantidade de mensagens
    count = 50  # Padrão
    if context.args:
        try:
            count = int(context.args[0])
        except ValueError:
            pass
    
    if not user_id:
        await update.message.reply_text(
            responses.INVALID_SYNTAX.format(
                syntax="/purge @usuario {quantidade} ou responda a uma mensagem com /purge {quantidade}"
            )
        )
        return
    
    progress_msg = await update.message.reply_text(responses.PURGE_IN_PROGRESS)
    
    deleted_count = 0
    current_message_id = update.message.message_id
    
    try:
        # Procura mensagens do usuário
        for offset in range(0, min(count * 10, 1000)):
            msg_id = current_message_id - offset
            if msg_id < 1:
                break
            
            try:
                # Tenta obter informações da mensagem
                message = await context.bot.forward_message(
                    chat_id=update.effective_chat.id,
                    from_chat_id=update.effective_chat.id,
                    message_id=msg_id
                )
                
                # Se a mensagem é do usuário alvo, deleta
                if message.forward_from and message.forward_from.id == user_id:
                    await context.bot.delete_message(update.effective_chat.id, msg_id)
                    deleted_count += 1
                
                # Deleta a mensagem encaminhada
                await context.bot.delete_message(update.effective_chat.id, message.message_id)
                
                if deleted_count >= count:
                    break
                    
            except TelegramError:
                pass
        
        await progress_msg.edit_text(
            responses.PURGE_SUCCESS.format(
                count=deleted_count,
                user=user_mention or f"ID:{user_id}"
            )
        )
        
    except Exception as e:
        await progress_msg.edit_text(f"{responses.OPERATION_FAILED}\nErro: {str(e)}")


def register_moderation_handlers(application) -> None:
    """Registra todos os handlers de moderação"""
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("kick", kick_command))
    application.add_handler(CommandHandler("mute", mute_command))
    application.add_handler(CommandHandler("unmute", unmute_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("nuke", nuke_command))
    application.add_handler(CommandHandler("purge", purge_command))
