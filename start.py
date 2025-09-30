"""
Inicia ambos os serviços (OAuth + Bot) em um único processo
Necessário para o plano free do Render que não suporta background workers
"""
import os
import threading
import logging
from src.oauth_server import app
from src.bot import main as bot_main

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def run_oauth_server():
    """Roda o servidor OAuth em uma thread separada"""
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Iniciando servidor OAuth na porta {port}...")
    app.run(host="0.0.0.0", port=port, use_reloader=False)

def run_telegram_bot():
    """Roda o bot do Telegram em uma thread separada"""
    logger.info("Iniciando bot do Telegram...")
    bot_main()

if __name__ == "__main__":
    logger.info("=== Iniciando sistema completo ===")
    
    oauth_thread = threading.Thread(target=run_oauth_server, daemon=True)
    oauth_thread.start()
    logger.info("✓ Thread do servidor OAuth iniciada")
    
    try:
        run_telegram_bot()
    except KeyboardInterrupt:
        logger.info("Encerrando sistema...")
