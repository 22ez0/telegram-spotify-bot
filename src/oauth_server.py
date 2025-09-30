"""
Servidor OAuth para autenticação Spotify por usuário
Agora também inclui webhook do Telegram
"""
import logging
import os
import secrets
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional
import aiohttp
from quart import Quart, request, redirect, jsonify
from sqlalchemy import select
from telegram import Update
from src.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
from src.database.db import db
from src.database.models import SpotifyAccount, User

logger = logging.getLogger(__name__)

app = Quart(__name__)

# Telegram bot application (será inicializado depois)
bot_application = None
webhook_secret_token = None

pending_auth_states: Dict[str, int] = {}

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_SCOPES = "user-read-currently-playing user-read-recently-played user-top-read user-read-playback-state"


def generate_auth_url(telegram_user_id: int) -> str:
    """Gera URL de autenticação do Spotify com state único"""
    state = secrets.token_urlsafe(32)
    pending_auth_states[state] = telegram_user_id
    
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": SPOTIFY_SCOPES,
        "state": state,
        "show_dialog": "true"
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{SPOTIFY_AUTH_URL}?{query_string}"


@app.route("/auth/spotify")
async def spotify_auth():
    """Redireciona usuário para autorização do Spotify"""
    telegram_user_id = request.args.get("user_id")
    
    if not telegram_user_id:
        return "Erro: ID do usuário não fornecido", 400
    
    try:
        telegram_user_id = int(telegram_user_id)
        auth_url = generate_auth_url(telegram_user_id)
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"Erro ao gerar URL de autenticação: {e}")
        return "Erro ao gerar link de autenticação", 500


@app.route("/callback/spotify")
async def spotify_callback():
    """Recebe callback do Spotify após autorização"""
    code = request.args.get("code")
    state = request.args.get("state")
    error = request.args.get("error")
    
    if error:
        return f"❌ Erro na autenticação: {error}", 400
    
    if not code or not state:
        return "❌ Código ou state não fornecido", 400
    
    telegram_user_id = pending_auth_states.pop(state, None)
    if not telegram_user_id:
        return "❌ State inválido ou expirado", 400
    
    try:
        auth_header = base64.b64encode(
            f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
        ).decode()
        
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": SPOTIFY_REDIRECT_URI
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(SPOTIFY_TOKEN_URL, headers=headers, data=data) as response:
                if response.status != 200:
                    error_data = await response.text()
                    logger.error(f"Erro ao obter token: {error_data}")
                    return "❌ Erro ao obter token de acesso", 500
                
                token_data = await response.json()
        
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        expires_in = token_data["expires_in"]
        
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        spotify_user_info = await get_spotify_user_info(access_token)
        
        async with db.session_maker() as db_session:
            stmt = select(SpotifyAccount).where(SpotifyAccount.user_id == telegram_user_id)
            result = await db_session.execute(stmt)
            existing_account = result.scalar_one_or_none()
            
            if existing_account:
                existing_account.access_token = access_token
                existing_account.refresh_token = refresh_token
                existing_account.token_expires_at = expires_at
                existing_account.spotify_user_id = spotify_user_info.get("id")
                existing_account.spotify_display_name = spotify_user_info.get("display_name")
            else:
                new_account = SpotifyAccount(
                    user_id=telegram_user_id,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_expires_at=expires_at,
                    spotify_user_id=spotify_user_info.get("id"),
                    spotify_display_name=spotify_user_info.get("display_name")
                )
                db_session.add(new_account)
            
            await db_session.commit()
        
        return """
        <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body { font-family: Arial; text-align: center; padding: 50px; background: #1DB954; color: white; }
                    h1 { font-size: 48px; margin-bottom: 20px; }
                    p { font-size: 24px; }
                </style>
            </head>
            <body>
                <h1>✅ Conectado!</h1>
                <p>Sua conta do Spotify foi conectada com sucesso!</p>
                <p>Você pode fechar esta janela e voltar ao Telegram.</p>
            </body>
        </html>
        """
        
    except Exception as e:
        logger.error(f"Erro ao processar callback: {e}")
        return f"❌ Erro ao processar autenticação: {str(e)}", 500


async def get_spotify_user_info(access_token: str) -> Dict:
    """Obtém informações do usuário do Spotify"""
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.spotify.com/v1/me", headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                return {}
    except Exception as e:
        logger.error(f"Erro ao obter info do usuário: {e}")
        return {}


async def refresh_user_token(user_id: int) -> Optional[str]:
    """Atualiza o token de acesso de um usuário"""
    try:
        async with db.session_maker() as session:
            stmt = select(SpotifyAccount).where(SpotifyAccount.user_id == user_id)
            result = await session.execute(stmt)
            account = result.scalar_one_or_none()
            
            if not account:
                return None
            
            if datetime.utcnow() < account.token_expires_at:
                return account.access_token
            
            auth_header = base64.b64encode(
                f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
            ).decode()
            
            headers = {
                "Authorization": f"Basic {auth_header}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "refresh_token",
                "refresh_token": account.refresh_token
            }
            
            async with aiohttp.ClientSession() as http_session:
                async with http_session.post(SPOTIFY_TOKEN_URL, headers=headers, data=data) as response:
                    if response.status != 200:
                        logger.error(f"Erro ao renovar token para user {user_id}")
                        return None
                    
                    token_data = await response.json()
            
            new_access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            new_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            account.access_token = new_access_token
            account.token_expires_at = new_expires_at
            
            if "refresh_token" in token_data:
                account.refresh_token = token_data["refresh_token"]
            
            await session.commit()
            
            return new_access_token
            
    except Exception as e:
        logger.error(f"Erro ao renovar token: {e}")
        return None


async def get_user_access_token(user_id: int) -> Optional[str]:
    """Obtém o token de acesso de um usuário (com refresh automático se necessário)"""
    return await refresh_user_token(user_id)


@app.route("/health")
async def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})


@app.route("/")
async def root():
    """Root endpoint para Render detectar a porta"""
    return jsonify({
        "status": "running",
        "service": "Telegram Bot & Spotify OAuth Server",
        "endpoints": {
            "health": "/health",
            "webhook": "/webhook",
            "spotify_auth": "/auth/spotify",
            "spotify_callback": "/callback/spotify"
        }
    })


@app.route("/webhook", methods=["POST"])
async def telegram_webhook():
    """Recebe atualizações do Telegram via webhook com validação de segurança"""
    if not bot_application:
        logger.error("Bot application não inicializado!")
        return jsonify({"error": "Bot not initialized"}), 500
    
    # Valida token secreto do Telegram
    telegram_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if webhook_secret_token and telegram_secret != webhook_secret_token:
        logger.warning(f"Tentativa de acesso não autorizado ao webhook")
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        json_data = await request.get_json()
        update = Update.de_json(json_data, bot_application.bot)
        await bot_application.update_queue.put(update)
        return jsonify({"ok": True})
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {e}")
        return jsonify({"error": str(e)}), 500


def set_bot_application(application, secret_token=None):
    """Define a aplicação do bot para o servidor"""
    global bot_application, webhook_secret_token
    bot_application = application
    webhook_secret_token = secret_token
    logger.info("Bot application configurado no servidor web")
    if secret_token:
        logger.info("🔒 Validação de webhook ativada")


def run_oauth_server():
    """Inicia o servidor OAuth"""
    port = 8080
    app.run(host="0.0.0.0", port=port)
