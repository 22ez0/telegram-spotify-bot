"""
Servidor principal com Webhook do Telegram + OAuth do Spotify
Otimizado para deployment no Render
"""
import os
import logging
import asyncio
import signal
import secrets
from src.bot import create_application
from src.oauth_server import app, set_bot_application
from src.config import get_oauth_base_url

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token secreto para validação de webhooks
WEBHOOK_SECRET_TOKEN = os.getenv('WEBHOOK_SECRET_TOKEN') or secrets.token_urlsafe(32)
bot_app = None


async def setup_webhook(bot_app):
    """Configura o webhook do Telegram com validação de segurança"""
    webhook_url = f"{get_oauth_base_url()}/webhook"
    
    try:
        # Remove webhook anterior se existir
        await bot_app.bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook anterior removido")
        
        # Configura novo webhook com token secreto
        await bot_app.bot.set_webhook(
            url=webhook_url,
            allowed_updates=["message", "edited_message", "callback_query", "inline_query"],
            secret_token=WEBHOOK_SECRET_TOKEN
        )
        logger.info(f"✅ Webhook configurado: {webhook_url}")
        logger.info(f"🔒 Token de segurança configurado")
        
        # Verifica webhook
        webhook_info = await bot_app.bot.get_webhook_info()
        logger.info(f"Webhook Info: {webhook_info}")
        
    except Exception as e:
        logger.error(f"Erro ao configurar webhook: {e}")
        raise


async def shutdown(signal_name=None):
    """Desligamento gracioso do servidor"""
    global bot_app
    
    if signal_name:
        logger.info(f"Recebido sinal {signal_name}, encerrando...")
    else:
        logger.info("Encerrando servidor...")
    
    if bot_app:
        try:
            await bot_app.bot.delete_webhook(drop_pending_updates=False)
            logger.info("Webhook removido")
        except:
            pass
        
        try:
            await bot_app.stop()
            await bot_app.shutdown()
            logger.info("Bot application encerrado")
        except Exception as e:
            logger.error(f"Erro ao encerrar bot: {e}")


async def main():
    """Função principal assíncrona"""
    global bot_app
    
    logger.info("=== Iniciando sistema completo ===")
    
    # Configura handlers de sinais para shutdown gracioso
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda s=sig: asyncio.create_task(shutdown(s.name))
        )
    
    try:
        # Cria e inicializa a aplicação do bot
        logger.info("Criando aplicação do bot...")
        bot_app = create_application()
        
        logger.info("Inicializando bot application...")
        await bot_app.initialize()
        await bot_app.start()
        
        # Configura webhook
        logger.info("Configurando webhook do Telegram...")
        await setup_webhook(bot_app)
        
        # Configura o bot no servidor web (inclui token de validação)
        set_bot_application(bot_app, WEBHOOK_SECRET_TOKEN)
        
        # Obtém porta do ambiente (Render usa PORT)
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"✅ Servidor pronto na porta {port}")
        logger.info("✅ Bot configurado e aguardando webhooks")
        
        # Roda servidor Quart
        await app.run_task(host="0.0.0.0", port=port)
        
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        raise
    finally:
        await shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Encerrando servidor...")
    except Exception as e:
        logger.error(f"Erro: {e}")
        raise
