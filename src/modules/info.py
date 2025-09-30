"""
Módulo de informações - Comandos para exibir dados de usuários e grupos
"""
from datetime import datetime
from telegram import Update, User as TgUser
from telegram.ext import ContextTypes, CommandHandler
from telegram.error import TelegramError

from src.utils.permissions import get_user_from_message
from src.utils.responses import responses


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /info - Exibe informações de usuário"""
    if not update.message or not update.effective_chat:
        return
    
    # Verifica se é para obter info de outro usuário
    user_id, user_mention = get_user_from_message(update)
    
    # Se não encontrou usuário mencionado/reply, usa o próprio usuário
    if not user_id:
        if context.args and context.args[0].isdigit():
            user_id = int(context.args[0])
        else:
            user_id = update.effective_user.id if update.effective_user else None
    
    if not user_id:
        await update.message.reply_text("Usuário não identificado. Use /info, /info @usuario ou /info {ID}")
        return
    
    try:
        # Obtém informações do usuário
        user = await context.bot.get_chat(user_id)
        
        # Monta texto de informações
        info_text = "INFORMAÇÕES DO USUÁRIO\n\n"
        info_text += f"ID: {user.id}\n"
        info_text += f"Nome: {user.first_name}"
        if user.last_name:
            info_text += f" {user.last_name}"
        info_text += "\n"
        
        if user.username:
            info_text += f"Username: @{user.username}\n"
        
        if user.bio:
            info_text += f"Bio: {user.bio}\n"
        
        # Informações adicionais do chat
        try:
            member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
            info_text += f"\nStatus no grupo: {member.status}\n"
            
            if member.status in ["administrator", "creator"]:
                info_text += "Cargo: Administrador\n"
        except Exception:
            pass
        
        # Tenta obter foto de perfil
        try:
            photos = await context.bot.get_user_profile_photos(user_id, limit=1)
            if photos.total_count > 0:
                photo = photos.photos[0][0]
                await update.message.reply_photo(
                    photo=photo.file_id,
                    caption=info_text
                )
                return
        except Exception:
            pass
        
        # Se não tem foto, envia só o texto
        await update.message.reply_text(info_text)
        
    except TelegramError as e:
        await update.message.reply_text(f"Falha ao obter informações do usuário.\nErro: {str(e)}")


async def chatinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /chatinfo - Exibe informações do grupo"""
    if not update.message or not update.effective_chat:
        return
    
    chat = update.effective_chat
    
    # Verifica se é um grupo
    if chat.type == "private":
        await update.message.reply_text("Este comando só funciona em grupos.")
        return
    
    try:
        # Obtém informações completas do chat
        chat_full = await context.bot.get_chat(chat.id)
        
        # Conta membros
        member_count = await context.bot.get_chat_member_count(chat.id)
        
        # Obtém lista de administradores
        admins = await context.bot.get_chat_administrators(chat.id)
        admin_list = []
        creator = None
        
        for admin in admins:
            if admin.status == "creator":
                creator = admin.user
            else:
                admin_list.append(admin.user)
        
        # Monta texto de informações
        info_text = "INFORMAÇÕES DO GRUPO\n\n"
        info_text += f"Nome: {chat_full.title}\n"
        info_text += f"ID: {chat_full.id}\n"
        info_text += f"Tipo: {chat_full.type}\n"
        
        if chat_full.username:
            info_text += f"Username: @{chat_full.username}\n"
        
        if chat_full.description:
            info_text += f"\nDescrição: {chat_full.description}\n"
        
        info_text += f"\nMembros: {member_count}\n"
        
        if creator:
            creator_name = creator.first_name
            if creator.username:
                creator_name += f" (@{creator.username})"
            info_text += f"Criador: {creator_name}\n"
        
        if admin_list:
            info_text += f"\nAdministradores ({len(admin_list)}):\n"
            for admin in admin_list[:10]:  # Limita a 10 para não ficar muito grande
                admin_name = admin.first_name
                if admin.username:
                    admin_name += f" (@{admin.username})"
                info_text += f"• {admin_name}\n"
            
            if len(admin_list) > 10:
                info_text += f"... e mais {len(admin_list) - 10}\n"
        
        # Informações de convite
        if chat_full.invite_link:
            info_text += f"\nLink de convite: {chat_full.invite_link}\n"
        
        # Tenta obter foto do grupo
        try:
            chat_photo = await context.bot.get_chat(chat.id)
            if chat_photo.photo:
                # Obtém a foto do chat
                photo_file = await context.bot.get_file(chat_photo.photo.big_file_id)
                await update.message.reply_photo(
                    photo=photo_file.file_id,
                    caption=info_text
                )
                return
        except Exception:
            pass
        
        # Se não tem foto, envia só o texto
        await update.message.reply_text(info_text)
        
    except TelegramError as e:
        await update.message.reply_text(f"Falha ao obter informações do grupo.\nErro: {str(e)}")


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /id - Exibe ID do usuário ou grupo"""
    if not update.message or not update.effective_chat:
        return
    
    # Verifica se é para obter ID de outro usuário
    user_id, user_mention = get_user_from_message(update)
    
    if user_id:
        await update.message.reply_text(f"ID do usuário: {user_id}")
    else:
        # Mostra IDs do usuário e do chat
        info_text = f"Seu ID: {update.effective_user.id}\n"
        info_text += f"ID deste chat: {update.effective_chat.id}"
        await update.message.reply_text(info_text)


def register_info_handlers(application) -> None:
    """Registra handlers de informações"""
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("chatinfo", chatinfo_command))
    application.add_handler(CommandHandler("id", id_command))
