"""
Servidor OAuth para autenticação do Spotify
"""
import os
from src.oauth_server import app

if __name__ == "__main__":
    # Render usa a variável PORT, Replit usa 5000
    port = int(os.environ.get('PORT', 5000))
    print(f"Iniciando servidor OAuth na porta {port}...")
    app.run(host="0.0.0.0", port=port)
