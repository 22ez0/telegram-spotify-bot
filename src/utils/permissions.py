"""
Utilitários para verificação de permissões
"""
from telegram import Update, ChatMember, ChatMemberAdministrator
from telegram.ext import ContextTypes


async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Verifica se o usuário é administrador"""
    if not update.effective_chat or not update.effective_user:
        return False
    
    try:
        member = await context.bot.get_chat_member(
            update.effective_chat.id,
            update.effective_user.id
        )
        return member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except Exception:
        return False


async def bot_can_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Verifica se o bot pode deletar mensagens"""
    if not update.effective_chat:
        return False
    
    try:
        bot_member = await context.bot.get_chat_member(
            update.effective_chat.id,
            context.bot.id
        )
        if bot_member.status == ChatMember.ADMINISTRATOR:
            if isinstance(bot_member, ChatMemberAdministrator):
                return bot_member.can_delete_messages or False
        return bot_member.status == ChatMember.OWNER
    except Exception:
        return False


async def bot_can_restrict(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Verifica se o bot pode restringir usuários"""
    if not update.effective_chat:
        return False
    
    try:
        bot_member = await context.bot.get_chat_member(
            update.effective_chat.id,
            context.bot.id
        )
        if bot_member.status == ChatMember.ADMINISTRATOR:
            if isinstance(bot_member, ChatMemberAdministrator):
                return bot_member.can_restrict_members or False
        return bot_member.status == ChatMember.OWNER
    except Exception:
        return False


def get_user_from_message(update: Update) -> tuple[int | None, str | None]:
    """Extrai ID e menção do usuário da mensagem ou reply"""
    # Se é reply, pega o usuário da mensagem original
    if update.message and update.message.reply_to_message:
        replied_user = update.message.reply_to_message.from_user
        if replied_user:
            mention = f"@{replied_user.username}" if replied_user.username else replied_user.first_name
            return replied_user.id, mention
    
    # Se não é reply, procura por menção no texto
    if update.message and update.message.entities and update.message.text:
        for entity in update.message.entities:
            if entity.type == "mention":
                username = update.message.text[entity.offset:entity.offset + entity.length]
                return None, username
            elif entity.type == "text_mention" and entity.user:
                user = entity.user
                mention = f"@{user.username}" if user.username else user.first_name
                return user.id, mention
    
    return None, None
