#!/usr/bin/env python3
"""
Script de verificação de configuração para Render
Exibe todas as informações necessárias para configurar o bot
"""
import os
import sys

def check_config():
    print("=" * 60)
    print("🔍 VERIFICAÇÃO DE CONFIGURAÇÃO - TELEGRAM BOT")
    print("=" * 60)
    print()
    
    # Verifica BOT_TOKEN
    bot_token = os.getenv("BOT_TOKEN", "")
    if bot_token:
        print("✅ BOT_TOKEN configurado")
        print(f"   Bot ID: {bot_token.split(':')[0]}")
    else:
        print("❌ BOT_TOKEN NÃO CONFIGURADO!")
        print("   Configure no Render: Environment → BOT_TOKEN")
        return False
    
    print()
    
    # Verifica Spotify
    spotify_id = os.getenv("SPOTIFY_CLIENT_ID", "")
    spotify_secret = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    
    if spotify_id and spotify_secret:
        print("✅ Credenciais do Spotify configuradas")
        print(f"   Client ID: {spotify_id[:20]}...")
    else:
        print("⚠️  Spotify não configurado (opcional)")
        print("   Configure SPOTIFY_CLIENT_ID e SPOTIFY_CLIENT_SECRET")
    
    print()
    
    # Detecta URL do servidor
    render_url = os.getenv("RENDER_EXTERNAL_URL", "")
    manual_uri = os.getenv("SPOTIFY_REDIRECT_URI", "")
    replit_domain = os.getenv("REPLIT_DEV_DOMAIN", "")
    
    detected_url = None
    detection_method = None
    
    if manual_uri:
        detected_url = manual_uri
        detection_method = "SPOTIFY_REDIRECT_URI (Manual)"
    elif render_url:
        detected_url = render_url
        detection_method = "RENDER_EXTERNAL_URL (Automático)"
    elif replit_domain:
        detected_url = f"https://{replit_domain}"
        detection_method = "REPLIT_DEV_DOMAIN (Desenvolvimento)"
    else:
        detected_url = "http://localhost:8080"
        detection_method = "Localhost (Fallback)"
    
    print("🌐 URL DO SERVIDOR DETECTADA:")
    print(f"   URL: {detected_url}")
    print(f"   Método: {detection_method}")
    print()
    
    # Monta URLs importantes
    webhook_url = f"{detected_url}/webhook"
    spotify_callback_url = f"{detected_url}/callback/spotify"
    auth_url = f"{detected_url}/auth/spotify?user_id=USER_ID"
    health_url = f"{detected_url}/health"
    
    print("📍 ENDPOINTS CONFIGURADOS:")
    print(f"   Webhook Telegram: {webhook_url}")
    print(f"   Callback Spotify: {spotify_callback_url}")
    print(f"   Health Check: {health_url}")
    print()
    
    # Instruções para Spotify
    if spotify_id and spotify_secret:
        print("=" * 60)
        print("🎵 CONFIGURAÇÃO DO SPOTIFY DEVELOPER DASHBOARD")
        print("=" * 60)
        print()
        print("1. Acesse: https://developer.spotify.com/dashboard")
        print("2. Selecione seu app")
        print("3. Clique em 'Edit Settings'")
        print("4. No campo 'Redirect URIs', adicione:")
        print()
        print(f"   {spotify_callback_url}")
        print()
        print("5. Clique em 'Save'")
        print()
        print("⚠️  IMPORTANTE: Sem este passo, o Spotify OAuth NÃO vai funcionar!")
        print()
    
    # Instruções adicionais
    if "render.com" in detected_url or "onrender.com" in detected_url:
        print("=" * 60)
        print("📦 DEPLOY NO RENDER")
        print("=" * 60)
        print()
        print("✅ Detectado ambiente Render!")
        print()
        print("Variáveis de ambiente necessárias no Render:")
        print("  • BOT_TOKEN (obrigatório)")
        print("  • SPOTIFY_CLIENT_ID (para integração Spotify)")
        print("  • SPOTIFY_CLIENT_SECRET (para integração Spotify)")
        print("  • OPENAI_API_KEY (opcional - para IA)")
        print("  • GOOGLE_API_KEY (opcional - para pesquisa)")
        print("  • GOOGLE_CSE_ID (opcional - para pesquisa)")
        print()
        print("💡 O Render fornece RENDER_EXTERNAL_URL automaticamente.")
        print("   Você NÃO precisa configurar SPOTIFY_REDIRECT_URI!")
        print()
    
    # Status final
    print("=" * 60)
    print("✅ VERIFICAÇÃO CONCLUÍDA")
    print("=" * 60)
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = check_config()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erro durante verificação: {e}")
        sys.exit(1)
