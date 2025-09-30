"""
Servidor principal com Webhook do Telegram + OAuth do Spotify
Otimizado para deployment no Render
"""
import os
import logging
import asyncio
from src.bot import create_application
from src.oauth_server import app, set_bot_application
from src.config import get_oauth_base_url

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def setup_webhook(bot_app):
    """Configura o webhook do Telegram"""
    webhook_url = f"{get_oauth_base_url()}/webhook"
    
    try:
        # Remove webhook anterior se existir
        await bot_app.bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook anterior removido")
        
        # Configura novo webhook
        await bot_app.bot.set_webhook(
            url=webhook_url,
            allowed_updates=["message", "edited_message", "callback_query", "inline_query"]
        )
        logger.info(f"✅ Webhook configurado: {webhook_url}")
        
        # Verifica webhook
        webhook_info = await bot_app.bot.get_webhook_info()
        logger.info(f"Webhook Info: {webhook_info}")
        
    except Exception as e:
        logger.error(f"Erro ao configurar webhook: {e}")
        raise


async def main():
    """Função principal assíncrona"""
    logger.info("=== Iniciando sistema completo ===")
    
    # Cria e inicializa a aplicação do bot
    logger.info("Criando aplicação do bot...")
    bot_app = create_application()
    
    logger.info("Inicializando bot application...")
    await bot_app.initialize()
    await bot_app.start()
    
    # Configura webhook
    logger.info("Configurando webhook do Telegram...")
    await setup_webhook(bot_app)
    
    # Configura o bot no servidor web
    set_bot_application(bot_app)
    
    # Obtém porta do ambiente (Render usa PORT)
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"✅ Servidor pronto na porta {port}")
    logger.info("✅ Bot configurado e aguardando webhooks")
    
    # Roda servidor Quart
    await app.run_task(host="0.0.0.0", port=port)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Encerrando servidor...")
