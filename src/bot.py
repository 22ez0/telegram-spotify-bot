"""
Bot de Telegram Principal
Arquitetura modular com Python-Telegram-Bot v20+ e asyncio
"""
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from src.config import BOT_TOKEN
from src.database.db import db
from src.modules.moderation import register_moderation_handlers
from src.modules.automod import register_automod_handlers
from src.modules.configuration import register_configuration_handlers
from src.modules.rank import register_rank_handlers
from src.modules.ai import register_ai_handlers
from src.modules.info import register_info_handlers
from src.modules.spotify_music import register_spotify_handlers

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuração de segurança: ocultar token nos logs
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('telegram.ext').setLevel(logging.WARNING)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start"""
    if not update.message:
        return
    
    welcome_text = (
        "Sistema de Moderação e Gerenciamento de Grupos\n\n"
        "Comandos disponíveis:\n\n"
        "Moderação:\n"
        "/ban - Banir usuário\n"
        "/kick - Remover usuário\n"
        "/mute - Silenciar usuário\n"
        "/unmute - Remover silenciamento\n"
        "/unban - Remover banimento\n"
        "/nuke - Deletar todas as mensagens\n"
        "/purge - Remover mensagens de usuário\n\n"
        "Informações:\n"
        "/info - Ver informações de usuário\n"
        "/chatinfo - Ver informações do grupo\n"
        "/id - Ver seu ID\n\n"
        "Configuração:\n"
        "/configuracoes - Painel de configurações\n\n"
        "Sistema de Rank:\n"
        "/rank - Ver sua posição\n\n"
        "IA e Pesquisa:\n"
        "/gerarimagem - Gerar imagem\n"
        "/pesquisar - Pesquisar na web\n"
        "/perguntar - Fazer pergunta à IA\n\n"
        "Spotify - Música:\n"
        "/conectarspotify - Conectar sua conta Spotify\n"
        ".fm - Ver o que você está ouvindo\n"
        ".profile - Seu perfil musical\n"
        ".chart - Gráficos das suas tops\n"
        ".plays - Histórico de reproduções\n"
        ".w - Estatísticas semanais\n"
        ".whoknows [artista] - Top ouvintes do grupo\n"
        ".crowns - Ranking de crowns do grupo\n"
        ".friends - Ver amigos ouvindo\n"
        "/adicionaramigo - Adicionar amigo\n\n"
        "Use /ajuda para mais informações."
    )
    
    await update.message.reply_text(welcome_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /ajuda"""
    if not update.message:
        return
    
    help_text = (
        "Manual de Operação do Sistema\n\n"
        "MODERAÇÃO:\n"
        "/ban @usuario {motivo} - Banir permanentemente\n"
        "/kick @usuario - Remover do grupo\n"
        "/mute @usuario {tempo} - Silenciar (ex: 5 minutos)\n"
        "/unmute @usuario - Remover silenciamento\n"
        "/unban @usuario - Remover banimento\n"
        "/nuke - Deletar todo histórico do grupo\n"
        "/purge @usuario {quantidade} - Remover mensagens específicas\n\n"
        "Todos os comandos de moderação podem ser usados respondendo a uma mensagem.\n\n"
        "INFORMAÇÕES:\n"
        "/info - Ver suas informações\n"
        "/info @usuario - Ver informações de outro usuário\n"
        "/info {ID} - Ver informações por ID\n"
        "/chatinfo - Ver informações completas do grupo\n"
        "/id - Ver seu ID e do chat\n\n"
        "CONFIGURAÇÃO:\n"
        "/configuracoes - Acessar painel de configurações interativo\n\n"
        "RANK:\n"
        "/rank - Ver sua posição no ranking do grupo\n\n"
        "IA E PESQUISA:\n"
        "/gerarimagem {descrição} - Gerar imagem com IA\n"
        "/pesquisar {consulta} - Pesquisar na web\n"
        "/perguntar {pergunta} - Consultar IA\n\n"
        "SPOTIFY - INTEGRAÇÃO MUSICAL:\n"
        "Fui desenvolvido por: @vgsswon com propósito de interação com seu spotify!\n"
        "Para seus amigos escutar músicas que você escuta no dia a dia!\n\n"
        "**Primeiros Passos:**\n"
        "/conectarspotify - Conectar sua conta do Spotify (obrigatório)\n\n"
        "**Comandos Principais:**\n"
        ".fm - Mostra a música que você está ouvindo agora com capa\n"
        ".profile - Seu perfil musical com estatísticas\n"
        ".chart [w/m/y] - Gráficos das suas tops (semanal, mensal, anual)\n"
        ".plays - Histórico das últimas reproduções\n"
        ".w - Estatísticas das últimas 4 semanas\n\n"
        "**Comandos Sociais:**\n"
        ".whoknows [artista] - Top ouvintes deste artista no grupo\n"
        ".crowns - Ranking de quem tem mais crowns no grupo\n"
        ".friends - Ver o que seus amigos estão ouvindo\n"
        "/adicionaramigo - Adicionar amigo (responda msg ou mencione)\n\n"
        "**Pesquisa:**\n"
        "/pesquisarmusica {nome} - Buscar músicas\n"
        "/pesquisarartista {nome} - Buscar artistas\n"
        "/pesquisaralbum {nome} - Buscar álbuns\n\n"
        "Cada membro conecta sua própria conta e vê suas músicas pessoais!\n"
        "Use .fm para registrar suas músicas e competir por crowns.\n\n"
        "Observações:\n"
        "- Comandos de moderação exigem permissões de administrador\n"
        "- AutoMod pode ser configurado via /configuracoes\n"
        "- Todas as ações são registradas no banco de dados"
    )
    
    await update.message.reply_text(help_text)


async def post_init(application: Application) -> None:
    """Inicialização pós-startup"""
    logger.info("=" * 60)
    logger.info("🔧 INICIALIZANDO BANCO DE DADOS...")
    logger.info(f"📍 DATABASE_URL configurada: {str(db.engine.url).split('@')[0]}@...")
    
    try:
        await db.init_db()
        logger.info("✅ Banco de dados inicializado com sucesso!")
        logger.info("✅ Todas as tabelas foram criadas/verificadas!")
        logger.info("=" * 60)
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ ERRO ao inicializar banco de dados: {e}")
        logger.error("=" * 60)
        raise


def create_application() -> Application:
    """Cria e configura a aplicação do bot"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN não configurado! Configure a variável de ambiente BOT_TOKEN.")
        raise ValueError("BOT_TOKEN não configurado")
    
    # Cria aplicação
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    # Registra handlers básicos
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ajuda", help_command))
    
    # Registra handlers dos módulos
    logger.info("Registrando handlers de moderação...")
    register_moderation_handlers(application)
    
    logger.info("Registrando handlers de automod...")
    register_automod_handlers(application)
    
    logger.info("Registrando handlers de configuração...")
    register_configuration_handlers(application)
    
    logger.info("Registrando handlers de rank...")
    register_rank_handlers(application)
    
    logger.info("Registrando handlers de IA...")
    register_ai_handlers(application)
    
    logger.info("Registrando handlers de informações...")
    register_info_handlers(application)
    
    logger.info("Registrando handlers do Spotify...")
    register_spotify_handlers(application)
    
    logger.info("Bot configurado com sucesso!")
    
    return application


def main() -> None:
    """Função principal (para compatibilidade)"""
    application = create_application()
    logger.info("Iniciando bot em modo polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
