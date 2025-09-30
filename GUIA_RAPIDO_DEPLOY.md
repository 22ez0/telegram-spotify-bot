# 🚀 Guia Rápido: Criar Repositório e Deploy no Render

## ✅ Correções Aplicadas

**Problema do `.fm` CORRIGIDO!** ✅
- Os comandos com `.` (como `.fm`, `.w`, `.profile`, etc.) agora têm prioridade sobre outros handlers
- Quando você não estiver conectado ao Spotify, o bot avisará: "❌ Você precisa conectar sua conta do Spotify primeiro. Use /conectarspotify"
- Depois de conectar, os comandos funcionarão normalmente!

---

## 📋 Passo 1: Criar Repositório no GitHub (usando Replit)

O Replit tem uma integração direta com o GitHub que facilita muito:

1. **Abrir o painel Git no Replit:**
   - Clique no ícone **"Version control"** na barra lateral esquerda
   - Ou pressione `Ctrl + K` e digite "Git"

2. **Conectar ao GitHub:**
   - Clique em **"Connect to GitHub"** ou **"Create a Git Repo"**
   - Escolha **"GitHub"**
   - Autorize o Replit a acessar sua conta GitHub
   - Escolha se quer repositório **Público** ou **Privado**
   - Clique em **"Create Repository"**

3. **Pronto!** 🎉
   - O Replit criará automaticamente o repositório
   - Todos os arquivos serão enviados
   - Você verá o link do repositório no painel Git

---

## 🌐 Passo 2: Deploy no Render

1. **Acessar o Render:**
   - Vá para https://render.com
   - Faça login (ou crie uma conta grátis)

2. **Criar novo Blueprint:**
   - Clique em **"New +"** no canto superior direito
   - Escolha **"Blueprint"**

3. **Conectar o repositório:**
   - Conecte sua conta do GitHub
   - Selecione o repositório que você criou
   - O Render detectará automaticamente o arquivo `render.yaml`
   - Clique em **"Apply"**

4. **Configurar Variáveis de Ambiente:**

   O Render vai pedir as seguintes variáveis (copie do Replit):

   ### 🔑 Variáveis OBRIGATÓRIAS:
   - `BOT_TOKEN` - Token do seu bot (pegue do @BotFather)
   - `SPOTIFY_CLIENT_ID` - ID do app Spotify
   - `SPOTIFY_CLIENT_SECRET` - Secret do app Spotify
   - `SPOTIFY_REDIRECT_URI` - URL de callback (ex: `https://seu-app.onrender.com/callback/spotify`)

   ### 🤖 Variáveis OPCIONAIS (para IA):
   - `OPENAI_API_KEY` - Para gerar imagens
   - `GOOGLE_API_KEY` - Para pesquisas
   - `GOOGLE_CSE_ID` - ID do Google Custom Search

5. **Aguardar o Deploy:**
   - O Render vai instalar as dependências
   - Vai criar 2 serviços:
     - **spotify-oauth-server** (Web Service)
     - **telegram-bot** (Worker)
   - Aguarde até aparecer "Live" ✅

---

## 🎵 Passo 3: Configurar o Spotify

Após o deploy, você receberá uma URL tipo: `https://seu-app.onrender.com`

1. **Acessar Spotify Developer Dashboard:**
   - Vá para https://developer.spotify.com/dashboard
   - Selecione seu app

2. **Adicionar Redirect URI:**
   - Clique em **"Edit Settings"**
   - No campo **"Redirect URIs"**, adicione:
     ```
     https://seu-app.onrender.com/callback/spotify
     ```
   - Clique em **"Save"**

---

## 🧪 Passo 4: Testar o Bot

1. Abra o Telegram e procure seu bot
2. Envie `/start` para iniciar
3. Envie `/conectarspotify` para conectar sua conta
4. Teste com `.fm` - agora deve funcionar! 🎵

---

## ⚠️ Importante sobre o Plano Free

- O serviço "dorme" após 15 minutos de inatividade
- Leva ~30 segundos para "acordar" na primeira requisição
- O **Bot** (worker) fica sempre ativo ✅
- O **Servidor OAuth** só é usado quando alguém conecta o Spotify
- Você tem 750 horas grátis por mês (suficiente para 1 serviço 24/7)

---

## 💾 Sobre o Banco de Dados

⚠️ O Render Free não tem armazenamento persistente!

**Solução:** Migre para PostgreSQL (também grátis no Render):
1. No Render, crie um **PostgreSQL Database** (free)
2. Copie a `DATABASE_URL` fornecida
3. Adicione como variável de ambiente no bot
4. O bot detectará e usará PostgreSQL automaticamente

---

## 🔧 Problemas Comuns

### Bot não responde
- Verifique se o token do Telegram está correto
- Veja os logs no Render Dashboard

### OAuth não funciona
- Confirme que `SPOTIFY_REDIRECT_URI` está configurada em AMBOS os serviços
- Verifique se a URL está correta no Spotify Dashboard
- **Se o link de autorização não abrir corretamente:**
  1. No Render, vá no serviço **telegram-bot** (Worker)
  2. Adicione a variável `OAUTH_SERVER_URL` com o valor da URL do web service
     - Exemplo: `https://spotify-oauth-server.onrender.com`
  3. Reinicie o bot

### Comandos `.fm` não funcionam
- ✅ JÁ CORRIGIDO! Os handlers agora têm prioridade
- Se ainda não funcionar, verifique se você conectou o Spotify com `/conectarspotify`

### Comandos de pesquisa falham com espaços
- ✅ JÁ CORRIGIDO! Queries agora são codificadas corretamente
- `/pesquisarmusica`, `/pesquisarartista`, `/pesquisaralbum` funcionam com espaços e caracteres especiais

---

## 📚 Links Úteis

- **GitHub:** https://github.com
- **Render:** https://render.com
- **Spotify Developer:** https://developer.spotify.com/dashboard
- **BotFather:** https://t.me/BotFather

---

## 🎉 Pronto!

Seu bot agora está:
- ✅ No GitHub (versionado)
- ✅ No Render (hospedado gratuitamente)
- ✅ Com comandos `.fm` funcionando corretamente
- ✅ Conectado ao Spotify

Divirta-se! 🎵🤖
