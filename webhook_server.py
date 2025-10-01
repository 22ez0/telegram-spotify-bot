"""
Servidor principal com Webhook do Telegram + OAuth do Spotify
Otimizado para deployment no Render
"""
import os
import logging
import asyncio
import signal
import secrets
from hypercorn.asyncio import serve
from hypercorn.config import Config
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
shutdown_event = asyncio.Event()


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
    
    # Sinaliza para parar o servidor
    shutdown_event.set()
    
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
    
    # Executa verificação de configuração
    logger.info("Verificando configuração...")
    import subprocess
    try:
        result = subprocess.run(
            ["python", "check_render_config.py"],
            capture_output=True,
            text=True,
            timeout=10
        )
        print(result.stdout)
        if result.returncode != 0:
            logger.warning("Verificação de configuração encontrou problemas")
    except Exception as e:
        logger.warning(f"Não foi possível executar verificação: {e}")
    
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
        
        # Inicializa banco de dados
        logger.info("=" * 60)
        logger.info("🔧 INICIALIZANDO BANCO DE DADOS...")
        from src.database.db import db
        from src.config import DATABASE_URL
        logger.info(f"📍 DATABASE_URL: {DATABASE_URL.split('@')[0] if '@' in DATABASE_URL else DATABASE_URL[:50]}...")
        try:
            await db.init_db()
            logger.info("✅ Banco de dados inicializado com sucesso!")
            logger.info("✅ Todas as tabelas foram criadas/verificadas!")
        except Exception as e:
            logger.error(f"❌ ERRO ao inicializar banco de dados: {e}")
            raise
        logger.info("=" * 60)
        
        await bot_app.start()
        
        # Configura webhook
        logger.info("Configurando webhook do Telegram...")
        await setup_webhook(bot_app)
        
        # Configura o bot no servidor web (inclui token de validação)
        set_bot_application(bot_app, WEBHOOK_SECRET_TOKEN)
        
        # Obtém porta do ambiente (Render usa PORT)
        port = int(os.environ.get('PORT', 5000))
        
        # Configura Hypercorn
        config = Config()
        config.bind = [f"0.0.0.0:{port}"]
        config.graceful_timeout = 30
        
        logger.info(f"✅ Servidor pronto na porta {port}")
        logger.info("✅ Bot configurado e aguardando webhooks")
        
        # Roda servidor com shutdown event
        await serve(app, config, shutdown_trigger=shutdown_event.wait)
        
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
