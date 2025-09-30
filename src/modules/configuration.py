"""
Módulo de configurações do bot
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from sqlalchemy import select

from src.utils.permissions import is_admin
from src.utils.responses import responses
from src.database.db import db
from src.database.models import Group


async def config_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /configuracoes - Menu principal de configurações"""
    if not update.message or not update.effective_chat:
        return
    
    if not await is_admin(update, context):
        await update.message.reply_text(responses.NO_PERMISSION)
        return
    
    keyboard = [
        [InlineKeyboardButton("Configurar Boas-Vindas", callback_data="config_welcome")],
        [InlineKeyboardButton("Configurar AutoMod", callback_data="config_automod")],
        [InlineKeyboardButton("Definir Canal de Log", callback_data="config_log")],
        [InlineKeyboardButton("Definir Fuso Horário", callback_data="config_timezone")],
        [InlineKeyboardButton("Fechar", callback_data="config_close")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Painel de Configurações do Grupo\n\nSelecione uma opção abaixo:",
        reply_markup=reply_markup
    )


async def config_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para callbacks de configuração"""
    query = update.callback_query
    if not query or not query.message:
        return
    
    await query.answer()
    
    if query.data == "config_close":
        await query.message.delete()
        return
    
    if query.data == "config_welcome":
        keyboard = [
            [InlineKeyboardButton("Habilitar Boas-Vindas", callback_data="welcome_enable")],
            [InlineKeyboardButton("Desabilitar Boas-Vindas", callback_data="welcome_disable")],
            [InlineKeyboardButton("Voltar", callback_data="config_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            "Configurações de Boas-Vindas\n\nSelecione uma opção:",
            reply_markup=reply_markup
        )
    
    elif query.data == "config_automod":
        keyboard = [
            [InlineKeyboardButton("Habilitar AutoMod", callback_data="automod_enable")],
            [InlineKeyboardButton("Desabilitar AutoMod", callback_data="automod_disable")],
            [InlineKeyboardButton("Filtro de Links: ON", callback_data="automod_links_on")],
            [InlineKeyboardButton("Filtro de Links: OFF", callback_data="automod_links_off")],
            [InlineKeyboardButton("Filtro de Spam: ON", callback_data="automod_spam_on")],
            [InlineKeyboardButton("Filtro de Spam: OFF", callback_data="automod_spam_off")],
            [InlineKeyboardButton("Voltar", callback_data="config_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            "Configurações de AutoMod\n\nSelecione uma opção:",
            reply_markup=reply_markup
        )
    
    elif query.data == "config_back":
        keyboard = [
            [InlineKeyboardButton("Configurar Boas-Vindas", callback_data="config_welcome")],
            [InlineKeyboardButton("Configurar AutoMod", callback_data="config_automod")],
            [InlineKeyboardButton("Definir Canal de Log", callback_data="config_log")],
            [InlineKeyboardButton("Definir Fuso Horário", callback_data="config_timezone")],
            [InlineKeyboardButton("Fechar", callback_data="config_close")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            "Painel de Configurações do Grupo\n\nSelecione uma opção abaixo:",
            reply_markup=reply_markup
        )
    
    # Handlers de Welcome
    elif query.data in ["welcome_enable", "welcome_disable"]:
        enabled = query.data == "welcome_enable"
        
        if query.message.chat:
            async for session in db.get_session():
                group = await db.get_or_create_group(
                    session, 
                    query.message.chat.id, 
                    query.message.chat.title or "Unknown"
                )
                group.welcome_enabled = enabled
                await session.commit()
                break
        
        status = "habilitadas" if enabled else "desabilitadas"
        await query.message.edit_text(f"Boas-vindas {status} com êxito.")
    
    # Handlers de AutoMod
    elif query.data in ["automod_enable", "automod_disable"]:
        enabled = query.data == "automod_enable"
        
        if query.message.chat:
            async for session in db.get_session():
                group = await db.get_or_create_group(
                    session, 
                    query.message.chat.id, 
                    query.message.chat.title or "Unknown"
                )
                group.automod_enabled = enabled
                await session.commit()
                break
        
        status = "habilitado" if enabled else "desabilitado"
        await query.message.edit_text(f"AutoMod {status} com êxito.")
    
    elif query.data in ["automod_links_on", "automod_links_off"]:
        enabled = query.data == "automod_links_on"
        
        if query.message.chat:
            async for session in db.get_session():
                group = await db.get_or_create_group(
                    session, 
                    query.message.chat.id, 
                    query.message.chat.title or "Unknown"
                )
                group.filter_links = enabled
                await session.commit()
                break
        
        status = "habilitado" if enabled else "desabilitado"
        await query.message.edit_text(f"Filtro de links {status} com êxito.")
    
    elif query.data in ["automod_spam_on", "automod_spam_off"]:
        enabled = query.data == "automod_spam_on"
        
        if query.message.chat:
            async for session in db.get_session():
                group = await db.get_or_create_group(
                    session, 
                    query.message.chat.id, 
                    query.message.chat.title or "Unknown"
                )
                group.filter_spam = enabled
                await session.commit()
                break
        
        status = "habilitado" if enabled else "desabilitado"
        await query.message.edit_text(f"Filtro de spam {status} com êxito.")


def register_configuration_handlers(application) -> None:
    """Registra handlers de configuração"""
    application.add_handler(CommandHandler("configuracoes", config_command))
    application.add_handler(CallbackQueryHandler(config_callback, pattern="^config_"))
    application.add_handler(CallbackQueryHandler(config_callback, pattern="^welcome_"))
    application.add_handler(CallbackQueryHandler(config_callback, pattern="^automod_"))
