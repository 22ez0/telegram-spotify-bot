# Bot de Telegram - Moderação e Gerenciamento de Grupos

Bot profissional de moderação para Telegram desenvolvido com Python 3.11+, python-telegram-bot v20+ e SQLAlchemy 2.0+.

## Características Principais

### Arquitetura
- **Modular**: Código organizado em módulos independentes (moderação, automod, rank, IA, configurações)
- **Assíncrono**: Utiliza asyncio para máxima performance
- **Type-safe**: Tipagem estrita com type hints do Python
- **Banco de dados**: SQLite com suporte para PostgreSQL via asyncpg
- **Escalável**: Preparado para alto volume de mensagens

### Funcionalidades

#### 1. Moderação (src/modules/moderation.py)
Comandos exclusivos para administradores:

- `/ban @usuario {motivo}` - Banir usuário permanentemente
- `/kick @usuario` - Remover usuário do grupo
- `/mute @usuario {tempo}` - Silenciar usuário (ex: 5 minutos, 1 hora)
- `/unmute @usuario` - Remover silenciamento
- `/unban @usuario` - Remover banimento
- `/nuke` - Deletar todas as mensagens do grupo (comando crítico)
- `/purge @usuario {quantidade}` - Remover mensagens específicas de um usuário

**Suporte a Reply**: Todos os comandos podem ser usados respondendo a uma mensagem, sem necessidade de mencionar o usuário.

#### 2. AutoMod (src/modules/automod.py)
Sistema automático de moderação:

- Filtro de links configurável
- Detecção de spam
- Remoção automática de conteúdo inadequado
- Configurável via painel de configurações

#### 3. Sistema de Rank (src/modules/rank.py)
- Rastreamento automático de atividade
- Contador de mensagens por usuário
- `/rank` - Ver posição no ranking do grupo

#### 4. Integrações com IA (src/modules/ai.py)
- `/gerarimagem {prompt}` - Gerar imagens com DALL-E
- `/pesquisar {consulta}` - Buscar na web com Google
- `/perguntar {pergunta}` - Chat com GPT-4

#### 5. Configurações (src/modules/configuration.py)
Menu interativo com botões inline:
- Configurar boas-vindas
- Habilitar/desabilitar AutoMod
- Configurar filtros de links e spam
- Definir canal de log
- Configurar fuso horário

## Instalação

### Requisitos
- Python 3.11+
- Token do bot (obtido via @BotFather no Telegram)

### Dependências
```bash
pip install python-telegram-bot[all] sqlalchemy[asyncio] asyncpg python-dotenv aiohttp pillow aiosqlite
```

### Configuração

1. Configure o token do bot nas variáveis de ambiente:
   - Obtenha o token com @BotFather no Telegram
   - Adicione `BOT_TOKEN` nas secrets do Replit

2. (Opcional) Configure APIs de IA:
   - `OPENAI_API_KEY` - Para geração de imagem e chat
   - `GOOGLE_API_KEY` e `GOOGLE_CSE_ID` - Para pesquisa na web

### Executando

```bash
python main.py
```

## Estrutura do Projeto

```
.
├── main.py                      # Ponto de entrada
├── src/
│   ├── bot.py                   # Aplicação principal
│   ├── config.py                # Configurações
│   ├── database/
│   │   ├── models.py            # Modelos SQLAlchemy
│   │   └── db.py                # Gerenciamento do banco
│   ├── modules/
│   │   ├── moderation.py        # Comandos de moderação
│   │   ├── automod.py           # Sistema automático
│   │   ├── configuration.py     # Painel de configurações
│   │   ├── rank.py              # Sistema de ranking
│   │   └── ai.py                # Integrações com IA
│   └── utils/
│       ├── permissions.py       # Verificação de permissões
│       └── responses.py         # Respostas formais do bot
└── README.md
```

## Banco de Dados

### Modelos

- **User**: Informações de usuários
- **Group**: Configurações de grupos
- **GroupUser**: Relação usuário-grupo (para ranking)
- **ModerationLog**: Registro de ações de moderação

### SQLite vs PostgreSQL

Por padrão, o bot usa SQLite para simplicidade. Para usar PostgreSQL:

1. Configure a variável `DATABASE_URL` com formato PostgreSQL
2. O bot converterá automaticamente para asyncpg

## Estilo de Comunicação

Todas as respostas do bot seguem um estilo **formal e profissional**, sem uso de emojis:

- ✅ "Operação concluída com êxito."
- ❌ "Tudo certo! 😊"

## Segurança

- Verificação de permissões em todos os comandos administrativos
- Logs de todas as ações de moderação
- Proteção contra rate limiting da API do Telegram
- Validação de entradas do usuário

## Comandos Disponíveis

### Usuários
- `/start` - Iniciar bot e ver comandos
- `/ajuda` - Manual completo de comandos
- `/rank` - Ver posição no ranking

### Administradores
- `/ban`, `/kick`, `/mute`, `/unmute`, `/unban` - Moderação básica
- `/nuke` - Deletar todo histórico (CUIDADO!)
- `/purge` - Remover mensagens específicas
- `/configuracoes` - Painel de configurações

### IA (requer API keys)
- `/gerarimagem` - Gerar imagens
- `/pesquisar` - Buscar na web
- `/perguntar` - Chat com IA

## Performance

- Operações assíncronas para máxima eficiência
- Batch processing para deleção em massa
- Pool de conexões do banco de dados otimizado
- Rate limiting respeitado automaticamente

## Logs

Todas as ações de moderação são registradas no banco de dados com:
- ID do grupo
- ID do moderador
- ID do usuário alvo
- Ação realizada
- Motivo (se fornecido)
- Timestamp

## Licença

Este é um projeto desenvolvido para demonstração de capacidades técnicas.

## Suporte

Para questões técnicas, consulte a documentação do python-telegram-bot: https://docs.python-telegram-bot.org/
