# Como Criar o Repositório no GitHub

## Opção 1: Usando a Interface Web do GitHub (Mais Fácil)

1. **Acesse GitHub:**
   - Vá para https://github.com
   - Faça login na sua conta

2. **Criar Novo Repositório:**
   - Clique no botão **"+" no canto superior direito**
   - Selecione **"New repository"**

3. **Configurar o Repositório:**
   - **Repository name:** `telegram-spotify-bot` (ou o nome que preferir)
   - **Description:** Bot de Telegram com integração Spotify
   - **Visibility:** Escolha **Private** ou **Public**
   - ⚠️ **NÃO** marque "Add a README file"
   - ⚠️ **NÃO** adicione .gitignore ou licença (já temos no projeto)
   - Clique em **"Create repository"**

4. **Enviar o Código:**
   Depois de criar, o GitHub mostrará comandos. Use estes:

   ```bash
   # Se já tem git configurado
   git remote add origin https://github.com/SEU_USUARIO/telegram-spotify-bot.git
   git branch -M main
   git push -u origin main
   ```

   ⚠️ **Importante:** Substitua `SEU_USUARIO` pelo seu username do GitHub!

5. **Alternativa: Download e Upload Manual**
   
   Se git não funcionar, você pode:
   - Baixar este projeto como ZIP do Replit
   - Extrair os arquivos no seu computador
   - No GitHub, clicar em "uploading an existing file"
   - Arrastar todos os arquivos (exceto bot.db)

## Opção 2: Importar do Replit para GitHub

O Replit tem integração nativa com GitHub:

1. **Na barra lateral do Replit:**
   - Clique no ícone de **Git** (3 bolinhas conectadas)
   - Ou use Ctrl+K e digite "Git"

2. **Conectar ao GitHub:**
   - Clique em **"Create a Git Repo"**
   - Escolha **"GitHub"**
   - Autorize o Replit a acessar sua conta GitHub
   - Escolha se quer repositório público ou privado
   - Clique em **"Create Repository"**

3. **Pronto!**
   - O Replit criará automaticamente o repositório
   - Todos os arquivos serão enviados
   - Você verá o link do repositório no painel Git

## Importante: Arquivos que NÃO devem ir para o GitHub

O `.gitignore` já está configurado para ignorar:
- `bot.db` (banco de dados local)
- `.env` (variáveis secretas)
- `__pycache__/` (cache do Python)
- `.replit`, `replit.nix` (configurações do Replit)

## Depois de Criar o Repositório

1. **Copie a URL do repositório** (ex: `https://github.com/SEU_USUARIO/telegram-spotify-bot`)

2. **Use essa URL para fazer deploy no Render:**
   - Vá em https://render.com
   - Clique em **"New +" → "Blueprint"**
   - Conecte seu repositório GitHub
   - O Render detectará automaticamente o `render.yaml`

## Problemas Comuns

### "Repository already exists"
- O repositório já foi criado
- Use: `git remote set-url origin https://github.com/SEU_USUARIO/telegram-spotify-bot.git`

### "Permission denied"
- Configure SSH ou use HTTPS com token pessoal
- Ou use a opção de upload manual

### "Git não está configurado"
- Use a integração do Replit com GitHub (Opção 2)
- É a forma mais simples!

## Links Úteis

- **GitHub:** https://github.com
- **Render:** https://render.com
- **Documentação Git:** https://git-scm.com/doc
