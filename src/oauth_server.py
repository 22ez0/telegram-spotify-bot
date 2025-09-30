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


@app.route("/")
async def index():
    """Página inicial com informações do servidor"""
    from src.config import get_oauth_base_url, BOT_TOKEN
    
    base_url = get_oauth_base_url()
    bot_configured = bool(BOT_TOKEN)
    spotify_configured = bool(SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET)
    
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Telegram Bot - Status</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #f5f5f5; }}
            .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #0088cc; border-bottom: 2px solid #0088cc; padding-bottom: 10px; }}
            h2 {{ color: #333; margin-top: 30px; }}
            .status {{ padding: 10px; border-radius: 5px; margin: 10px 0; }}
            .status.ok {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }}
            .status.warning {{ background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }}
            .endpoint {{ background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 5px 0; font-family: monospace; }}
            .code {{ background: #e9ecef; padding: 15px; border-radius: 5px; font-family: monospace; margin: 10px 0; }}
            ul {{ line-height: 1.8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Telegram Bot - Servidor OAuth</h1>
            
            <h2>📊 Status do Sistema</h2>
            <div class="status {'ok' if bot_configured else 'warning'}">
                {'✅' if bot_configured else '⚠️'} Bot do Telegram: {'Configurado' if bot_configured else 'Não configurado'}
            </div>
            <div class="status {'ok' if spotify_configured else 'warning'}">
                {'✅' if spotify_configured else '⚠️'} Spotify OAuth: {'Configurado' if spotify_configured else 'Não configurado'}
            </div>
            
            <h2>🌐 URL Base Detectada</h2>
            <div class="code">{base_url}</div>
            
            <h2>📍 Endpoints Disponíveis</h2>
            <div class="endpoint">📡 Webhook: {base_url}/webhook</div>
            <div class="endpoint">🎵 Spotify Auth: {base_url}/auth/spotify?user_id=USER_ID</div>
            <div class="endpoint">✅ Callback: {base_url}/callback/spotify</div>
            <div class="endpoint">💚 Health: {base_url}/health</div>
            
            <h2>🎵 Configuração do Spotify</h2>
            <p>Para que o OAuth do Spotify funcione, adicione esta URL no Spotify Developer Dashboard:</p>
            <div class="code">{base_url}/callback/spotify</div>
            
            <h3>Passo a passo:</h3>
            <ol>
                <li>Acesse <a href="https://developer.spotify.com/dashboard" target="_blank">developer.spotify.com/dashboard</a></li>
                <li>Selecione seu app</li>
                <li>Clique em "Edit Settings"</li>
                <li>No campo "Redirect URIs", cole a URL acima</li>
                <li>Clique em "Save"</li>
            </ol>
            
            <h2>🔧 Variáveis de Ambiente Necessárias</h2>
            <ul>
                <li><strong>BOT_TOKEN</strong> - Token do bot (obrigatório)</li>
                <li><strong>SPOTIFY_CLIENT_ID</strong> - Client ID do Spotify</li>
                <li><strong>SPOTIFY_CLIENT_SECRET</strong> - Client Secret do Spotify</li>
                <li><strong>OPENAI_API_KEY</strong> - Para geração de imagens (opcional)</li>
                <li><strong>GOOGLE_API_KEY</strong> - Para pesquisa web (opcional)</li>
            </ul>
            
            <p style="margin-top: 30px; color: #666; text-align: center;">
                Bot desenvolvido para Telegram • Integração Spotify • Moderação de grupos
            </p>
        </div>
    </body>
    </html>
    """
    return html


@app.route("/health")
async def health_check():
    """Health check endpoint para monitoramento"""
    from src.config import get_oauth_base_url, BOT_TOKEN
    
    return jsonify({
        "status": "healthy",
        "bot_configured": bool(BOT_TOKEN),
        "spotify_configured": bool(SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET),
        "base_url": get_oauth_base_url(),
        "endpoints": {
            "webhook": "/webhook",
            "spotify_auth": "/auth/spotify",
            "spotify_callback": "/callback/spotify",
            "health": "/health"
        }
    })


@app.route("/debug/spotify")
async def debug_spotify():
    """Debug endpoint para verificar configuração do Spotify"""
    from src.config import get_oauth_base_url
    
    return jsonify({
        "spotify_client_id": SPOTIFY_CLIENT_ID[:20] + "..." if SPOTIFY_CLIENT_ID else "NOT SET",
        "spotify_client_secret_set": bool(SPOTIFY_CLIENT_SECRET),
        "spotify_redirect_uri": SPOTIFY_REDIRECT_URI,
        "base_url": get_oauth_base_url(),
        "expected_redirect_uri": f"{get_oauth_base_url()}/callback/spotify",
        "match": SPOTIFY_REDIRECT_URI == f"{get_oauth_base_url()}/callback/spotify",
        "scopes": SPOTIFY_SCOPES,
        "test_auth_url": f"/auth/spotify?user_id=123456789",
        "instructions": [
            "1. Copie o 'spotify_redirect_uri' exato acima",
            "2. Acesse https://developer.spotify.com/dashboard",
            "3. Selecione seu app > Edit Settings",
            "4. Cole a URI em 'Redirect URIs'",
            "5. Clique ADD e depois SAVE",
            "6. Aguarde 1-2 minutos para propagar"
        ]
    })


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
