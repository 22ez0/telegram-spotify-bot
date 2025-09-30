# Como Fazer Deploy no Render (GRÁTIS)

## Passo 1: Preparar o GitHub

1. Crie uma conta no GitHub (github.com) se não tiver
2. Crie um novo repositório (pode ser privado)
3. Faça push do seu código:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git
git push -u origin main
```

## Passo 2: Configurar o Render

1. Crie uma conta no Render (render.com) - é grátis!
2. No dashboard, clique em "New +" e escolha **"Blueprint"**
3. Conecte seu repositório do GitHub
4. O Render vai detectar o arquivo `render.yaml` automaticamente

## Passo 3: Configurar Variáveis de Ambiente

O Render vai pedir para você adicionar as seguintes variáveis:

### OBRIGATÓRIAS:
- **BOT_TOKEN**: Token do seu bot do Telegram (pegue com @BotFather)
- **SPOTIFY_CLIENT_ID**: ID do app no Spotify Developer Dashboard
- **SPOTIFY_CLIENT_SECRET**: Secret do app no Spotify Developer Dashboard
- **SPOTIFY_REDIRECT_URI**: URL de callback do OAuth (ex: `https://SEU-APP.onrender.com/callback/spotify`)

### OPCIONAIS (para recursos de IA):
- **OPENAI_API_KEY**: Para gerar imagens e perguntas
- **GOOGLE_API_KEY**: Para pesquisas na web
- **GOOGLE_CSE_ID**: ID do Custom Search Engine do Google

### 💡 IMPORTANTE: SPOTIFY_REDIRECT_URI
Esta variável DEVE ser configurada em AMBOS os serviços:
1. **spotify-oauth-server** (Web Service)
2. **telegram-bot** (Worker)

Sem ela, o bot não conseguirá gerar os links de autenticação do Spotify!

## Passo 4: Configurar o Spotify Dashboard

Após o deploy, o Render vai te dar uma URL do tipo:
```
https://spotify-oauth-server.onrender.com
```

1. Acesse [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Selecione seu app
3. Clique em **"Edit Settings"**
4. No campo **"Redirect URIs"**, adicione:
   ```
   https://SEU-APP.onrender.com/callback/spotify
   ```
5. Clique em **"Save"**

## Passo 5: Alternativas de Hosting para OAuth (Gratuito)

Se você não quiser usar o Render para o servidor OAuth, pode usar outras plataformas gratuitas:

### Opção 1: Render (Recomendado)
- Já configurado no `render.yaml`
- Free tier com 750 horas/mês
- Suporta Python nativamente
- URL: `https://SEU-APP.onrender.com/callback/spotify`

### Opção 2: Netlify (Alternativa)
1. Deploy o servidor OAuth no Netlify (na raiz do domínio)
2. Configure `OAUTH_SERVER_URL=https://SEU-APP.netlify.app` no Render (worker)
3. Configure `SPOTIFY_REDIRECT_URI=https://SEU-APP.netlify.app/callback/spotify` no Netlify
4. Adicione a URL no Spotify Dashboard

⚠️ **Importante:** O servidor deve rodar na raiz do domínio, não em subpaths!

### Opção 3: Vercel (Alternativa)
1. Deploy o servidor OAuth no Vercel (na raiz do domínio)
2. Configure `OAUTH_SERVER_URL=https://SEU-APP.vercel.app` no Render (worker)
3. Configure `SPOTIFY_REDIRECT_URI=https://SEU-APP.vercel.app/callback/spotify` no Vercel
4. Adicione a URL no Spotify Dashboard

### Opção 4: Cloudflare Pages (Alternativa)
1. Deploy o servidor OAuth no Cloudflare Pages (na raiz)
2. Configure `OAUTH_SERVER_URL=https://SEU-APP.pages.dev` no Render (worker)
3. Configure `SPOTIFY_REDIRECT_URI=https://SEU-APP.pages.dev/callback/spotify` no Cloudflare
4. Adicione a URL no Spotify Dashboard

### Como Funciona a Detecção Automática

O bot detecta automaticamente a URL do servidor OAuth nesta ordem:
1. **SPOTIFY_REDIRECT_URI** (manual, qualquer plataforma)
2. **RENDER_EXTERNAL_URL** (automático no Render)
3. **OAUTH_SERVER_URL** (manual, para Netlify/Vercel/etc)
4. **REPLIT_DOMAINS** (legado, Replit)

Basta configurar uma dessas variáveis!

## Importante sobre o Plano Gratuito

⚠️ **Limitações do Plano Free do Render:**
- O serviço "dorme" após 15 minutos de inatividade
- Leva ~30 segundos para "acordar" na primeira requisição
- Você tem 750 horas grátis por mês (suficiente para 1 serviço 24/7)

💡 **Como funciona:**
- O **Bot do Telegram** (worker) fica sempre ativo e responde imediatamente
- O **Servidor OAuth** só é usado quando alguém conecta a conta do Spotify
- Se o servidor OAuth estiver "dormindo", a primeira conexão pode demorar 30 segundos

## Estrutura dos Serviços

O `render.yaml` configura 2 serviços:

1. **spotify-oauth-server** (Web Service - Free)
   - Porta: Automática (variável $PORT)
   - Comando: `python run_oauth.py`
   - Usado apenas para autenticação OAuth

2. **telegram-bot** (Background Worker - Free)
   - Comando: `python main.py`
   - Roda 24/7 respondendo comandos do Telegram

## Testando o Deployment

Após o deploy:

1. Teste o bot no Telegram: `/start`
2. Conecte o Spotify: `/conectarspotify`
3. Teste um comando: `.fm`

Se algo não funcionar, veja os logs no Render Dashboard.

## Banco de Dados

⚠️ **Importante:** O Render Free não tem armazenamento persistente!

O bot usa SQLite (arquivo `bot.db`), mas esse arquivo será perdido quando o serviço reiniciar.

**Solução:** Migre para PostgreSQL (também tem plano free no Render):
1. No Render, crie um PostgreSQL Database (free)
2. Copie a `DATABASE_URL` fornecida
3. Adicione como variável de ambiente no bot
4. O bot vai detectar e usar PostgreSQL automaticamente

## Custos

- **Plano Free**: $0/mês
  - 750 horas grátis
  - Serviços dormem após inatividade
  - Sem armazenamento persistente

- **Plano Starter**: $7/mês (se quiser upgrade)
  - Sempre ativo
  - Sem sleep
  - Mais recursos

Para um bot pequeno, o plano Free é suficiente! 🎉
