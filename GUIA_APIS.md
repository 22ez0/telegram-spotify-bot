# Como Obter as APIs de IA

## OpenAI API (para /gerarimagem e /perguntar)

### Passo 1: Criar conta na OpenAI
1. Acesse: https://platform.openai.com/
2. Clique em "Sign up" e crie sua conta
3. Faça login na plataforma

### Passo 2: Obter a API Key
1. No menu lateral, clique em "API keys"
2. Clique em "Create new secret key"
3. Dê um nome para sua chave (ex: "Telegram Bot")
4. Copie a chave (ela só aparecerá uma vez!)
5. Guarde em local seguro

### Passo 3: Adicionar créditos
1. Acesse: https://platform.openai.com/account/billing
2. Clique em "Add payment method"
3. Adicione um cartão de crédito
4. Compre créditos (mínimo $5 USD)

### Passo 4: Configurar no Bot
- Adicione a chave nas secrets do Replit com o nome `OPENAI_API_KEY`
- O bot detectará automaticamente e habilitará os comandos

**Custos estimados:**
- `/gerarimagem` (DALL-E 3): ~$0.04 por imagem
- `/perguntar` (GPT-4): ~$0.03 por pergunta (500 tokens)

---

## Google Custom Search API (para /pesquisar)

### Parte 1: Google API Key

#### Passo 1: Criar projeto no Google Cloud
1. Acesse: https://console.cloud.google.com/
2. Clique em "Select a project" → "New Project"
3. Dê um nome ao projeto (ex: "Telegram Bot")
4. Clique em "Create"

#### Passo 2: Ativar a API
1. No menu lateral, vá em "APIs & Services" → "Library"
2. Busque por "Custom Search API"
3. Clique e depois em "Enable"

#### Passo 3: Criar credenciais
1. Vá em "APIs & Services" → "Credentials"
2. Clique em "Create Credentials" → "API Key"
3. Copie a chave gerada
4. (Opcional) Clique em "Restrict Key" para segurança
5. Em "API restrictions", selecione "Custom Search API"
6. Salve

### Parte 2: Google Custom Search Engine ID

#### Passo 1: Criar Search Engine
1. Acesse: https://programmablesearchengine.google.com/
2. Clique em "Add" ou "Create"
3. Em "Sites to search", adicione: `*` (para buscar em toda web)
4. Dê um nome (ex: "Bot Search")
5. Clique em "Create"

#### Passo 2: Obter o ID
1. Clique em "Control Panel" do seu search engine
2. Em "Setup" → "Basics", copie o "Search engine ID"

#### Passo 3: Configurar no Bot
Adicione nas secrets do Replit:
- `GOOGLE_API_KEY`: Sua API Key do Google Cloud
- `GOOGLE_CSE_ID`: O ID do Custom Search Engine

**Custos:**
- 100 buscas/dia GRÁTIS
- Após isso: $5 por 1000 buscas

---

## Resumo das Variáveis de Ambiente

Configure no Replit Secrets:

```
BOT_TOKEN=seu_token_do_botfather (OBRIGATÓRIO)
OPENAI_API_KEY=sua_chave_openai (OPCIONAL)
GOOGLE_API_KEY=sua_chave_google (OPCIONAL)
GOOGLE_CSE_ID=seu_search_engine_id (OPCIONAL)
```

**Nota:** O bot funciona normalmente sem as APIs de IA. Os comandos de IA simplesmente mostrarão uma mensagem informando que a API não está configurada.

---

## Testes Recomendados

Após configurar as APIs, teste:

1. **OpenAI:**
   - `/gerarimagem um gato astronauta`
   - `/perguntar O que é Python?`

2. **Google:**
   - `/pesquisar python programming`

Se houver erros, verifique:
- ✅ As chaves foram copiadas corretamente
- ✅ Não há espaços extras nas secrets
- ✅ As APIs estão ativadas no console
- ✅ Há créditos/quota disponível
