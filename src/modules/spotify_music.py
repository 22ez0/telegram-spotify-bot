"""
Módulo Spotify - fui desenvolvido por: @vgsswon com propósito de interação com seu spotify! para seus amigos escutar músicas que você escuta no dia a dia!
Mostra músicas que usuários estão ouvindo, estatísticas e permite pesquisas
COM AUTENTICAÇÃO POR USUÁRIO
"""
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
import aiohttp
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from sqlalchemy import select, delete, func
from src.database.db import db
from src.database.models import SpotifyTrack, SpotifyAccount, User, Group, UserFriend, ArtistCrown
from src.config import SPOTIFY_REDIRECT_URI

logger = logging.getLogger(__name__)


async def save_track_to_db(user_id: int, group_id: int, track_data: Dict[str, Any], user_data: Optional[Dict[str, Any]] = None, chat_title: Optional[str] = None) -> None:
    """Salva uma música tocada no banco de dados"""
    try:
        track = track_data
        track_id = track['id']
        track_name = track['name']
        artists = ", ".join([artist['name'] for artist in track['artists']])
        album_name = track['album']['name']
        album_image = track['album']['images'][0]['url'] if track['album']['images'] else None
        spotify_url = track['external_urls']['spotify']
        
        async with db.session_maker() as session:
            if user_data:
                await session.merge(User(
                    id=user_id,
                    first_name=user_data.get('first_name', 'Unknown'),
                    last_name=user_data.get('last_name'),
                    username=user_data.get('username')
                ))
            else:
                await session.merge(User(id=user_id, first_name="Unknown", username=None))
            
            await session.merge(Group(id=group_id, title=chat_title or "Unknown"))
            
            spotify_track = SpotifyTrack(
                user_id=user_id,
                group_id=group_id,
                track_id=track_id,
                track_name=track_name,
                artist_name=artists,
                album_name=album_name,
                album_image_url=album_image,
                spotify_url=spotify_url
            )
            
            session.add(spotify_track)
            await session.commit()
            
    except Exception as e:
        logger.error(f"Erro ao salvar música no banco: {e}")


async def get_user_spotify_token(user_id: int) -> Optional[str]:
    """Obtém o token de acesso do Spotify para um usuário específico (com refresh automático)"""
    try:
        async with db.session_maker() as session:
            stmt = select(SpotifyAccount).where(SpotifyAccount.user_id == user_id)
            result = await session.execute(stmt)
            account = result.scalar_one_or_none()
            
            if not account:
                return None
            
            if datetime.utcnow() < account.token_expires_at:
                return account.access_token
            
            from src.oauth_server import refresh_user_token
            return await refresh_user_token(user_id)
    except Exception as e:
        logger.error(f"Erro ao obter token do usuário: {e}")
        return None


async def get_current_playing(access_token: str) -> Optional[Dict[str, Any]]:
    """Obtém a música que está tocando atualmente"""
    try:
        url = "https://api.spotify.com/v1/me/player/currently-playing"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 204:
                    return None
                else:
                    logger.error(f"Erro ao buscar música atual: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"Erro ao buscar música atual: {e}")
        return None


async def get_recently_played(access_token: str, limit: int = 10) -> Optional[Dict[str, Any]]:
    """Obtém as músicas tocadas recentemente"""
    try:
        url = f"https://api.spotify.com/v1/me/player/recently-played?limit={limit}"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Erro ao buscar músicas recentes: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"Erro ao buscar músicas recentes: {e}")
        return None


async def search_track(access_token: str, query: str) -> Optional[Dict[str, Any]]:
    """Pesquisa por uma música"""
    try:
        url = "https://api.spotify.com/v1/search"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            "q": query,
            "type": "track",
            "limit": 5
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Erro ao pesquisar música: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"Erro ao pesquisar música: {e}")
        return None


async def search_artist(access_token: str, query: str) -> Optional[Dict[str, Any]]:
    """Pesquisa por um artista"""
    try:
        url = "https://api.spotify.com/v1/search"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            "q": query,
            "type": "artist",
            "limit": 5
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Erro ao pesquisar artista: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"Erro ao pesquisar artista: {e}")
        return None


async def search_album(access_token: str, query: str) -> Optional[Dict[str, Any]]:
    """Pesquisa por um álbum"""
    try:
        url = "https://api.spotify.com/v1/search"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            "q": query,
            "type": "album",
            "limit": 5
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Erro ao pesquisar álbum: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"Erro ao pesquisar álbum: {e}")
        return None


async def get_user_top_tracks(access_token: str, time_range: str = "medium_term", limit: int = 10) -> Optional[Dict[str, Any]]:
    """Obtém as músicas mais ouvidas do usuário"""
    try:
        url = f"https://api.spotify.com/v1/me/top/tracks?time_range={time_range}&limit={limit}"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Erro ao buscar top músicas: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"Erro ao buscar top músicas: {e}")
        return None


async def get_user_top_artists(access_token: str, time_range: str = "medium_term", limit: int = 10) -> Optional[Dict[str, Any]]:
    """Obtém os artistas mais ouvidos do usuário"""
    try:
        url = f"https://api.spotify.com/v1/me/top/artists?time_range={time_range}&limit={limit}"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Erro ao buscar top artistas: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"Erro ao buscar top artistas: {e}")
        return None


async def connect_spotify_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /conectarspotify - Gera link único para o usuário conectar sua conta"""
    if not update.message or not update.message.from_user:
        return
    
    user_id = update.message.from_user.id
    
    try:
        async with db.session_maker() as session:
            stmt = select(SpotifyAccount).where(SpotifyAccount.user_id == user_id)
            result = await session.execute(stmt)
            existing_account = result.scalar_one_or_none()
            
            if existing_account:
                message = (
                    "✅ **Sua conta do Spotify já está conectada!**\n\n"
                    "Você já pode usar todos os comandos:\n"
                    "• .fm - Ver o que está ouvindo agora\n"
                    "• .profile - Seu perfil musical\n"
                    "• .chart - Gráficos das suas tops\n"
                    "• .plays - Histórico de reproduções\n"
                    "• .w - Estatísticas semanais\n\n"
                    "Para desconectar, use /desconectarspotify"
                )
                await update.message.reply_text(message, parse_mode='Markdown')
                return
    except Exception as e:
        logger.error(f"Erro ao verificar conta existente: {e}")
    
    # Usa a mesma lógica de detecção automática do servidor OAuth
    from src.config import get_oauth_base_url
    try:
        base_url = get_oauth_base_url()
        
        # Verifica se está em produção sem configuração adequada
        if base_url == "http://localhost:8080":
            # Detecta se está em ambiente de produção (várias plataformas)
            is_production = bool(
                os.getenv("RENDER") or  # Render (worker e web service)
                os.getenv("RENDER_EXTERNAL_URL") or 
                os.getenv("RENDER_SERVICE_ID") or
                os.getenv("RAILWAY_PUBLIC_DOMAIN") or
                os.getenv("RAILWAY_ENVIRONMENT") or
                os.getenv("FLY_APP_NAME") or
                os.getenv("HEROKU_APP_NAME") or
                os.getenv("VERCEL_URL") or
                os.getenv("NETLIFY") or
                os.getenv("CF_PAGES") or  # Cloudflare Pages
                os.getenv("CF_PAGES_URL") or
                os.getenv("BOT_ENV") == "production"
            )
            
            if is_production:
                logger.error("OAuth servidor não configurado em produção!")
                await update.message.reply_text(
                    "❌ Erro: O servidor OAuth não está configurado.\n"
                    "Configure SPOTIFY_REDIRECT_URI ou OAUTH_SERVER_URL no ambiente.\n"
                    "Consulte a documentação para instruções de deploy."
                )
                return
            else:
                # Desenvolvimento local - permite mas avisa
                logger.warning("Usando localhost para OAuth - apenas para desenvolvimento!")
        
        if not base_url:
            await update.message.reply_text(
                "❌ Erro ao detectar servidor OAuth. Entre em contato com o administrador."
            )
            return
    except Exception as e:
        logger.error(f"Erro ao obter URL do OAuth: {e}")
        await update.message.reply_text(
            "❌ Erro ao gerar link de autorização. Entre em contato com o administrador."
        )
        return
    
    auth_url = f"{base_url}/auth/spotify?user_id={user_id}"
    
    message = (
        "🎵 **Conectar sua conta do Spotify**\n\n"
        "Para usar os comandos do Spotify, você precisa conectar sua conta pessoal.\n\n"
        f"👉 [Clique aqui para autorizar]({auth_url})\n\n"
        "Você será redirecionado para o Spotify onde poderá autorizar o acesso.\n"
        "Após autorizar, volte aqui e use os comandos!\n\n"
        "**Comandos disponíveis após conectar:**\n"
        "• .fm - Ver o que você está ouvindo\n"
        "• .profile - Seu perfil musical\n"
        "• .chart - Gráficos das suas tops\n"
        "• .plays - Histórico de reproduções\n"
        "• .w - Estatísticas semanais"
    )
    
    await update.message.reply_text(message, parse_mode='Markdown', disable_web_page_preview=False)


async def disconnect_spotify_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /desconectarspotify - Remove vinculação da conta do usuário"""
    if not update.message or not update.message.from_user:
        return
    
    user_id = update.message.from_user.id
    
    try:
        async with db.session_maker() as session:
            stmt = delete(SpotifyAccount).where(SpotifyAccount.user_id == user_id)
            result = await session.execute(stmt)
            await session.commit()
            
            if result.rowcount > 0:
                await update.message.reply_text(
                    "✅ Sua conta do Spotify foi desconectada com sucesso.\n"
                    "Use /conectarspotify para conectar novamente."
                )
            else:
                await update.message.reply_text(
                    "❌ Você não tem nenhuma conta do Spotify conectada.\n"
                    "Use /conectarspotify para conectar sua conta."
                )
    except Exception as e:
        logger.error(f"Erro ao desconectar conta: {e}")
        await update.message.reply_text("❌ Erro ao desconectar sua conta. Tente novamente.")


async def fm_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando .fm / /fm - Mostra a música que o usuário está ouvindo"""
    if not update.message or not update.message.from_user:
        return
    
    user_id = update.message.from_user.id
    
    access_token = await get_user_spotify_token(user_id)
    if not access_token:
        await update.message.reply_text(
            "❌ Você precisa conectar sua conta do Spotify primeiro.\n"
            "Use /conectarspotify para conectar sua conta."
        )
        return
    
    current = await get_current_playing(access_token)
    
    if not current or not current.get('item'):
        recent = await get_recently_played(access_token, limit=1)
        if recent and recent.get('items'):
            track = recent['items'][0]['track']
            is_recent = True
        else:
            await update.message.reply_text("🎵 Você não está ouvindo nada no Spotify no momento.")
            return
    else:
        track = current['item']
        is_recent = False
    
    group_id = update.message.chat.id
    
    user_data = {
        'first_name': update.message.from_user.first_name,
        'last_name': update.message.from_user.last_name,
        'username': update.message.from_user.username
    }
    chat_title = update.message.chat.title
    
    await save_track_to_db(user_id, group_id, track, user_data, chat_title)
    
    track_name = track['name']
    artists = ", ".join([artist['name'] for artist in track['artists']])
    album_name = track['album']['name']
    album_image = track['album']['images'][0]['url'] if track['album']['images'] else None
    track_url = track['external_urls']['spotify']
    
    user_name = update.message.from_user.first_name
    status = f"🎵 {user_name} ouviu recentemente:" if is_recent else f"🎵 {user_name} está ouvindo agora:"
    
    caption = (
        f"{status}\n\n"
        f"🎼 **{track_name}**\n"
        f"👤 {artists}\n"
        f"💿 {album_name}\n\n"
        f"[Abrir no Spotify]({track_url})"
    )
    
    if album_image:
        await update.message.reply_photo(
            photo=album_image,
            caption=caption,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(caption, parse_mode='Markdown')


async def weekly_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando .w / /w - Mostra estatísticas semanais"""
    if not update.message or not update.message.from_user:
        return
    
    user_id = update.message.from_user.id
    
    access_token = await get_user_spotify_token(user_id)
    if not access_token:
        await update.message.reply_text(
            "❌ Você precisa conectar sua conta do Spotify primeiro.\n"
            "Use /conectarspotify para conectar sua conta."
        )
        return
    
    top_tracks = await get_user_top_tracks(access_token, "short_term", 10)
    top_artists = await get_user_top_artists(access_token, "short_term", 5)
    
    if not top_tracks or not top_artists:
        await update.message.reply_text("❌ Não foi possível obter suas estatísticas.")
        return
    
    user_name = update.message.from_user.first_name
    text = f"📊 **Estatísticas de {user_name} das últimas 4 semanas:**\n\n"
    
    text += "🎵 **Top 10 Músicas:**\n"
    for i, track in enumerate(top_tracks.get('items', []), 1):
        track_name = track['name']
        artists = ", ".join([artist['name'] for artist in track['artists']])
        text += f"{i}. {track_name} - {artists}\n"
    
    text += "\n👤 **Top 5 Artistas:**\n"
    for i, artist in enumerate(top_artists.get('items', []), 1):
        text += f"{i}. {artist['name']}\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def search_music_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /pesquisarmusica - Pesquisa por músicas"""
    if not update.message or not update.message.from_user:
        return
    
    if not context.args:
        await update.message.reply_text("❌ Use: /pesquisarmusica <nome da música>")
        return
    
    user_id = update.message.from_user.id
    query = " ".join(context.args)
    
    access_token = await get_user_spotify_token(user_id)
    if not access_token:
        await update.message.reply_text(
            "❌ Você precisa conectar sua conta do Spotify primeiro.\n"
            "Use /conectarspotify para conectar sua conta."
        )
        return
    
    results = await search_track(access_token, query)
    
    if not results or not results.get('tracks', {}).get('items'):
        await update.message.reply_text(f"❌ Nenhuma música encontrada para: {query}")
        return
    
    text = f"🔍 **Resultados para '{query}':**\n\n"
    
    for i, track in enumerate(results['tracks']['items'][:5], 1):
        track_name = track['name']
        artists = ", ".join([artist['name'] for artist in track['artists']])
        album = track['album']['name']
        url = track['external_urls']['spotify']
        text += f"{i}. [{track_name}]({url})\n   👤 {artists}\n   💿 {album}\n\n"
    
    await update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True)


async def search_artist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /pesquisarartista - Pesquisa por artistas"""
    if not update.message or not update.message.from_user:
        return
    
    if not context.args:
        await update.message.reply_text("❌ Use: /pesquisarartista <nome do artista>")
        return
    
    user_id = update.message.from_user.id
    query = " ".join(context.args)
    
    access_token = await get_user_spotify_token(user_id)
    if not access_token:
        await update.message.reply_text(
            "❌ Você precisa conectar sua conta do Spotify primeiro.\n"
            "Use /conectarspotify para conectar sua conta."
        )
        return
    
    results = await search_artist(access_token, query)
    
    if not results or not results.get('artists', {}).get('items'):
        await update.message.reply_text(f"❌ Nenhum artista encontrado para: {query}")
        return
    
    text = f"🔍 **Artistas encontrados para '{query}':**\n\n"
    
    for i, artist in enumerate(results['artists']['items'][:5], 1):
        name = artist['name']
        followers = artist['followers']['total']
        url = artist['external_urls']['spotify']
        genres = ", ".join(artist['genres'][:3]) if artist['genres'] else "N/A"
        text += f"{i}. [{name}]({url})\n   👥 {followers:,} seguidores\n   🎸 {genres}\n\n"
    
    await update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True)


async def search_album_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /pesquisaralbum - Pesquisa por álbuns"""
    if not update.message or not update.message.from_user:
        return
    
    if not context.args:
        await update.message.reply_text("❌ Use: /pesquisaralbum <nome do álbum>")
        return
    
    user_id = update.message.from_user.id
    query = " ".join(context.args)
    
    access_token = await get_user_spotify_token(user_id)
    if not access_token:
        await update.message.reply_text(
            "❌ Você precisa conectar sua conta do Spotify primeiro.\n"
            "Use /conectarspotify para conectar sua conta."
        )
        return
    
    results = await search_album(access_token, query)
    
    if not results or not results.get('albums', {}).get('items'):
        await update.message.reply_text(f"❌ Nenhum álbum encontrado para: {query}")
        return
    
    text = f"🔍 **Álbuns encontrados para '{query}':**\n\n"
    
    for i, album in enumerate(results['albums']['items'][:5], 1):
        name = album['name']
        artists = ", ".join([artist['name'] for artist in album['artists']])
        release_date = album['release_date']
        total_tracks = album['total_tracks']
        url = album['external_urls']['spotify']
        text += f"{i}. [{name}]({url})\n   👤 {artists}\n   📅 {release_date}\n   🎵 {total_tracks} músicas\n\n"
    
    await update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True)


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando .profile / /profile - Mostra perfil do usuário com estatísticas"""
    if not update.message or not update.message.from_user:
        return
    
    user_id = update.message.from_user.id
    
    access_token = await get_user_spotify_token(user_id)
    if not access_token:
        await update.message.reply_text(
            "❌ Você precisa conectar sua conta do Spotify primeiro.\n"
            "Use /conectarspotify para conectar sua conta."
        )
        return
    
    top_artists = await get_user_top_artists(access_token, "long_term", 1)
    top_tracks = await get_user_top_tracks(access_token, "long_term", 50)
    
    if not top_artists or not top_tracks:
        await update.message.reply_text("❌ Erro ao buscar suas estatísticas.")
        return
    
    top_artist = "N/A"
    if top_artists.get('items'):
        top_artist = top_artists['items'][0]['name']
    
    total_plays = len(top_tracks.get('items', []))
    
    user_name = update.message.from_user.first_name
    username = f"@{update.message.from_user.username}" if update.message.from_user.username else ""
    
    text = (
        f"👤 **Perfil de {user_name}** {username}\n\n"
        f"🎤 **Artista favorito (all time):** {top_artist}\n"
        f"📊 **Top tracks registradas:** {total_plays}\n\n"
        f"Use .chart para ver seus gráficos\n"
        f"Use .w para ver suas estatísticas semanais\n"
        f"Use .plays para ver seu histórico"
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def plays_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando .plays / /plays - Mostra histórico recente de reproduções"""
    if not update.message or not update.message.from_user:
        return
    
    user_id = update.message.from_user.id
    
    access_token = await get_user_spotify_token(user_id)
    if not access_token:
        await update.message.reply_text(
            "❌ Você precisa conectar sua conta do Spotify primeiro.\n"
            "Use /conectarspotify para conectar sua conta."
        )
        return
    
    recent = await get_recently_played(access_token, limit=10)
    
    if not recent or not recent.get('items'):
        await update.message.reply_text("🎵 Você não tem histórico de reproduções recentes.")
        return
    
    user_name = update.message.from_user.first_name
    text = f"🎵 **Últimas reproduções de {user_name}:**\n\n"
    
    for i, item in enumerate(recent['items'], 1):
        track = item['track']
        track_name = track['name']
        artists = ", ".join([artist['name'] for artist in track['artists']])
        album = track['album']['name']
        url = track['external_urls']['spotify']
        text += f"{i}. [{track_name}]({url})\n"
        text += f"   👤 {artists}\n"
        text += f"   💿 {album}\n\n"
    
    await update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True)


async def chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando .chart / /chart - Mostra gráfico de top artistas e músicas"""
    if not update.message or not update.message.from_user:
        return
    
    user_id = update.message.from_user.id
    
    access_token = await get_user_spotify_token(user_id)
    if not access_token:
        await update.message.reply_text(
            "❌ Você precisa conectar sua conta do Spotify primeiro.\n"
            "Use /conectarspotify para conectar sua conta."
        )
        return
    
    time_range = "short_term"
    if context.args and len(context.args) > 0:
        period = context.args[0].lower()
        if period in ['w', 'weekly', 'semanal']:
            time_range = "short_term"
        elif period in ['m', 'monthly', 'mensal']:
            time_range = "medium_term"
        elif period in ['y', 'yearly', 'anual', 'a', 'alltime']:
            time_range = "long_term"
    
    top_tracks = await get_user_top_tracks(access_token, time_range, 5)
    top_artists = await get_user_top_artists(access_token, time_range, 5)
    
    if not top_tracks or not top_artists:
        await update.message.reply_text("❌ Não foi possível gerar seus gráficos.")
        return
    
    user_name = update.message.from_user.first_name
    
    period_name = "últimas 4 semanas"
    if time_range == "medium_term":
        period_name = "últimos 6 meses"
    elif time_range == "long_term":
        period_name = "de todos os tempos"
    
    text = f"📊 **Gráfico de {user_name} ({period_name}):**\n\n"
    
    text += "🎵 **Top 5 Músicas:**\n"
    for i, track in enumerate(top_tracks.get('items', [])[:5], 1):
        track_name = track['name']
        artists = ", ".join([artist['name'] for artist in track['artists']])
        text += f"{i}. {track_name} - {artists}\n"
    
    text += "\n👤 **Top 5 Artistas:**\n"
    for i, artist in enumerate(top_artists.get('items', [])[:5], 1):
        text += f"{i}. {artist['name']}\n"
    
    text += "\n💡 Use .chart w/m/y para diferentes períodos"
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def dot_fm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para detectar mensagens .fm"""
    if update.message and update.message.text and update.message.text.strip().startswith('.fm'):
        await fm_command(update, context)


async def dot_w_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para detectar mensagens .w"""
    if update.message and update.message.text and update.message.text.strip().startswith('.w'):
        await weekly_command(update, context)


async def dot_profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para detectar mensagens .profile"""
    if update.message and update.message.text and update.message.text.strip().startswith('.profile'):
        await profile_command(update, context)


async def dot_plays_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para detectar mensagens .plays"""
    if update.message and update.message.text and update.message.text.strip().startswith('.plays'):
        await plays_command(update, context)


async def dot_chart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para detectar mensagens .chart"""
    if update.message and update.message.text:
        text = update.message.text.strip()
        if text.startswith('.chart'):
            parts = text.split()
            if len(parts) > 1:
                context.args = parts[1:]
            await chart_command(update, context)


async def whoknows_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando .whoknows [artista] - Mostra top ouvintes de um artista no grupo"""
    if not update.message or not update.message.from_user:
        return
    
    if not context.args:
        await update.message.reply_text("❌ Use: .whoknows <nome do artista>")
        return
    
    artist_query = " ".join(context.args)
    group_id = update.message.chat.id
    
    try:
        async with db.session_maker() as session:
            stmt = select(
                SpotifyTrack.user_id,
                User.first_name,
                User.username,
                func.count(SpotifyTrack.id).label('play_count')
            ).join(
                User, SpotifyTrack.user_id == User.id
            ).where(
                SpotifyTrack.group_id == group_id,
                SpotifyTrack.artist_name.ilike(f"%{artist_query}%")
            ).group_by(
                SpotifyTrack.user_id,
                User.first_name,
                User.username
            ).order_by(
                func.count(SpotifyTrack.id).desc()
            ).limit(10)
            
            result = await session.execute(stmt)
            listeners = result.all()
            
            if not listeners:
                await update.message.reply_text(
                    f"❌ Ninguém no grupo ouviu **{artist_query}** ainda.\n"
                    f"Use .fm para registrar suas músicas!",
                    parse_mode='Markdown'
                )
                return
            
            chat_title = update.message.chat.title or "este grupo"
            text = f"👥 **Top ouvintes de {artist_query} em {chat_title}:**\n\n"
            
            for i, (user_id, first_name, username, count) in enumerate(listeners, 1):
                crown = "👑 " if i == 1 else ""
                user_display = f"{first_name}" + (f" (@{username})" if username else "")
                text += f"{crown}{i}. {user_display} - {count} plays\n"
            
            await update.message.reply_text(text, parse_mode='Markdown')
            
            if listeners:
                crown_user_id = listeners[0][0]
                artist_name = artist_query
                
                delete_stmt = delete(ArtistCrown).where(
                    ArtistCrown.group_id == group_id,
                    ArtistCrown.artist_name.ilike(f"%{artist_query}%")
                )
                await session.execute(delete_stmt)
                
                new_crown = ArtistCrown(
                    group_id=group_id,
                    user_id=crown_user_id,
                    artist_name=artist_name,
                    play_count=listeners[0][3]
                )
                session.add(new_crown)
                await session.commit()
                
    except Exception as e:
        logger.error(f"Erro ao buscar whoknows: {e}")
        await update.message.reply_text("❌ Erro ao buscar os dados.")


async def crowns_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando .crowns - Mostra ranking de crowns (artistas mais ouvidos) do grupo"""
    if not update.message or not update.message.from_user:
        return
    
    group_id = update.message.chat.id
    
    try:
        async with db.session_maker() as session:
            stmt = select(
                User.first_name,
                User.username,
                func.count(ArtistCrown.id).label('crown_count')
            ).join(
                User, ArtistCrown.user_id == User.id
            ).where(
                ArtistCrown.group_id == group_id
            ).group_by(
                User.id,
                User.first_name,
                User.username
            ).order_by(
                func.count(ArtistCrown.id).desc()
            ).limit(10)
            
            result = await session.execute(stmt)
            crown_holders = result.all()
            
            if not crown_holders:
                await update.message.reply_text(
                    "👑 Ainda não há crowns neste grupo!\n\n"
                    "Use .whoknows [artista] para começar a competir por crowns."
                )
                return
            
            chat_title = update.message.chat.title or "este grupo"
            text = f"👑 **Ranking de Crowns em {chat_title}:**\n\n"
            
            for i, (first_name, username, count) in enumerate(crown_holders, 1):
                user_display = f"{first_name}" + (f" (@{username})" if username else "")
                text += f"{i}. {user_display} - {count} 👑\n"
            
            await update.message.reply_text(text, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Erro ao buscar crowns: {e}")
        await update.message.reply_text("❌ Erro ao buscar os dados.")


async def friends_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando .friends - Mostra o que seus amigos estão ouvindo"""
    if not update.message or not update.message.from_user:
        return
    
    user_id = update.message.from_user.id
    
    try:
        async with db.session_maker() as session:
            stmt = select(UserFriend.friend_id).where(UserFriend.user_id == user_id)
            result = await session.execute(stmt)
            friend_ids = [row[0] for row in result.all()]
            
            if not friend_ids:
                await update.message.reply_text(
                    "👥 Você ainda não tem amigos adicionados.\n\n"
                    "Use /adicionaramigo <@usuario> para adicionar amigos\n"
                    "e ver o que eles estão ouvindo!"
                )
                return
            
            friends_listening = []
            for friend_id in friend_ids[:10]:
                friend_token = await get_user_spotify_token(friend_id)
                if not friend_token:
                    continue
                
                current = await get_current_playing(friend_token)
                if current and current.get('item'):
                    track = current['item']
                    
                    user_stmt = select(User).where(User.id == friend_id)
                    user_result = await session.execute(user_stmt)
                    friend_user = user_result.scalar_one_or_none()
                    
                    if friend_user:
                        friends_listening.append({
                            'name': friend_user.first_name,
                            'username': friend_user.username,
                            'track': track['name'],
                            'artist': ", ".join([a['name'] for a in track['artists']]),
                            'url': track['external_urls']['spotify']
                        })
            
            if not friends_listening:
                await update.message.reply_text(
                    "🎵 Nenhum dos seus amigos está ouvindo música no momento."
                )
                return
            
            text = "👥 **O que seus amigos estão ouvindo:**\n\n"
            for friend in friends_listening:
                user_display = f"{friend['name']}" + (f" (@{friend['username']})" if friend['username'] else "")
                text += f"🎵 **{user_display}**\n"
                text += f"   [{friend['track']}]({friend['url']})\n"
                text += f"   👤 {friend['artist']}\n\n"
            
            await update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True)
            
    except Exception as e:
        logger.error(f"Erro ao buscar amigos: {e}")
        await update.message.reply_text("❌ Erro ao buscar dados dos amigos.")


async def add_friend_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /adicionaramigo - Adiciona um amigo para acompanhar"""
    if not update.message or not update.message.from_user:
        return
    
    if not update.message.reply_to_message and not context.args:
        await update.message.reply_text(
            "❌ Use: /adicionaramigo respondendo a mensagem de alguém\n"
            "ou /adicionaramigo <@usuario>"
        )
        return
    
    user_id = update.message.from_user.id
    friend_id = None
    
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        friend_id = update.message.reply_to_message.from_user.id
    
    if friend_id == user_id:
        await update.message.reply_text("❌ Você não pode adicionar a si mesmo como amigo!")
        return
    
    try:
        async with db.session_maker() as session:
            existing = select(UserFriend).where(
                UserFriend.user_id == user_id,
                UserFriend.friend_id == friend_id
            )
            result = await session.execute(existing)
            if result.scalar_one_or_none():
                await update.message.reply_text("✅ Este usuário já está na sua lista de amigos!")
                return
            
            new_friend = UserFriend(
                user_id=user_id,
                friend_id=friend_id
            )
            session.add(new_friend)
            await session.commit()
            
            await update.message.reply_text(
                "✅ Amigo adicionado com sucesso!\n"
                "Use .friends para ver o que seus amigos estão ouvindo."
            )
            
    except Exception as e:
        logger.error(f"Erro ao adicionar amigo: {e}")
        await update.message.reply_text("❌ Erro ao adicionar amigo.")


async def dot_whoknows_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para detectar mensagens .whoknows"""
    if update.message and update.message.text:
        text = update.message.text.strip()
        if text.startswith('.whoknows'):
            parts = text.split(maxsplit=1)
            if len(parts) > 1:
                context.args = parts[1].split()
            await whoknows_command(update, context)


async def dot_crowns_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para detectar mensagens .crowns"""
    if update.message and update.message.text and update.message.text.strip().startswith('.crowns'):
        await crowns_command(update, context)


async def dot_friends_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para detectar mensagens .friends"""
    if update.message and update.message.text and update.message.text.strip().startswith('.friends'):
        await friends_command(update, context)


def register_spotify_handlers(application: Application) -> None:
    """Registra os handlers do módulo Spotify"""
    application.add_handler(CommandHandler("conectarspotify", connect_spotify_command))
    application.add_handler(CommandHandler("desconectarspotify", disconnect_spotify_command))
    application.add_handler(CommandHandler("adicionaramigo", add_friend_command))
    
    application.add_handler(CommandHandler("fm", fm_command))
    application.add_handler(CommandHandler("w", weekly_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("plays", plays_command))
    application.add_handler(CommandHandler("chart", chart_command))
    application.add_handler(CommandHandler("whoknows", whoknows_command))
    application.add_handler(CommandHandler("crowns", crowns_command))
    application.add_handler(CommandHandler("friends", friends_command))
    application.add_handler(CommandHandler("pesquisarmusica", search_music_command))
    application.add_handler(CommandHandler("pesquisarartista", search_artist_command))
    application.add_handler(CommandHandler("pesquisaralbum", search_album_command))
    
    application.add_handler(MessageHandler(filters.Regex(r'^\.fm\b'), dot_fm_handler), group=-1)
    application.add_handler(MessageHandler(filters.Regex(r'^\.w\b'), dot_w_handler), group=-1)
    application.add_handler(MessageHandler(filters.Regex(r'^\.profile\b'), dot_profile_handler), group=-1)
    application.add_handler(MessageHandler(filters.Regex(r'^\.plays\b'), dot_plays_handler), group=-1)
    application.add_handler(MessageHandler(filters.Regex(r'^\.chart\b'), dot_chart_handler), group=-1)
    application.add_handler(MessageHandler(filters.Regex(r'^\.whoknows\b'), dot_whoknows_handler), group=-1)
    application.add_handler(MessageHandler(filters.Regex(r'^\.crowns\b'), dot_crowns_handler), group=-1)
    application.add_handler(MessageHandler(filters.Regex(r'^\.friends\b'), dot_friends_handler), group=-1)
