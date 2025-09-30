"""
Configuração central do bot
"""
import os
from typing import Final
from dotenv import load_dotenv

load_dotenv()

# Token do Bot
BOT_TOKEN: Final[str] = os.getenv("BOT_TOKEN", "")

# Database - Usa SQLite por padrão para simplicidade
DATABASE_URL: Final[str] = "sqlite+aiosqlite:///bot.db"

# API Keys (Opcionais)
OPENAI_API_KEY: Final[str] = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY: Final[str] = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID: Final[str] = os.getenv("GOOGLE_CSE_ID", "")

# Spotify OAuth Credentials
SPOTIFY_CLIENT_ID: Final[str] = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET: Final[str] = os.getenv("SPOTIFY_CLIENT_SECRET", "")

# Gera automaticamente o SPOTIFY_REDIRECT_URI baseado na plataforma de hospedagem
def get_oauth_base_url() -> str:
    """Obtém a URL base do servidor OAuth automaticamente (apenas scheme://host)"""
    from urllib.parse import urlparse
    
    # Primeiro verifica se há uma URI configurada manualmente e extrai apenas scheme+host
    manual_uri = os.getenv("SPOTIFY_REDIRECT_URI", "")
    if manual_uri and not manual_uri.startswith("http://localhost"):
        # Extrai apenas scheme e netloc (host), ignorando path completamente
        parsed = urlparse(manual_uri)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    # Verifica se está no Render (web service)
    render_url = os.getenv("RENDER_EXTERNAL_URL", "")
    if render_url:
        return render_url.rstrip('/')
    
    # Verifica variável manual para qualquer plataforma (Netlify, Vercel, etc)
    custom_url = os.getenv("OAUTH_SERVER_URL", "")
    if custom_url:
        return custom_url.rstrip('/')
    
    # Verifica se está no Replit (legacy)
    replit_domains = os.getenv("REPLIT_DOMAINS", "")
    if replit_domains:
        domain = replit_domains.split(',')[0]
        return f"https://{domain}"
    
    replit_dev_domain = os.getenv("REPLIT_DEV_DOMAIN", "")
    if replit_dev_domain:
        return f"https://{replit_dev_domain}"
    
    # Fallback para desenvolvimento local
    return "http://localhost:8080"


def get_spotify_redirect_uri() -> str:
    """Gera a URI de redirecionamento do Spotify automaticamente"""
    # Se já está configurada manualmente, usa ela
    manual_uri = os.getenv("SPOTIFY_REDIRECT_URI", "")
    if manual_uri:
        return manual_uri
    
    # Caso contrário, gera automaticamente
    base_url = get_oauth_base_url()
    return f"{base_url}/callback/spotify"

SPOTIFY_REDIRECT_URI: Final[str] = get_spotify_redirect_uri()

# Configurações do Bot
MAX_MESSAGE_DELETE_BATCH: Final[int] = 100
RATE_LIMIT_DELAY: Final[float] = 0.5
NUKE_BATCH_SIZE: Final[int] = 100

# Permissões necessárias
ADMIN_COMMANDS: Final[set] = {
    "nuke", "purge", "ban", "kick", "mute", "unmute", 
    "unban", "configuracoes", "automod"
}
