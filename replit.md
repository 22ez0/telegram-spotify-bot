# Telegram Bot - Moderation and Group Management

## Overview

This is a professional Telegram moderation bot built with Python 3.11+, leveraging modern asynchronous architecture with python-telegram-bot v20+ and SQLAlchemy 2.0+. The bot provides comprehensive group management features including automated moderation, rank tracking, AI integrations (image generation, web search, chat), and administrative controls. It's designed for high-performance handling of large message volumes with a modular, scalable architecture.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Technology Stack

**Language & Runtime**
- Python 3.11+ with strict type hints and async/await patterns
- Fully asynchronous I/O using asyncio for maximum performance

**Telegram Integration**
- python-telegram-bot v20+ for bot API interactions
- Handlers for commands, callbacks, and message tracking
- Support for inline keyboards for interactive menus

**Database Layer**
- SQLAlchemy 2.0+ as the ORM with async support
- Default: SQLite with aiosqlite driver for simplicity
- Prepared for PostgreSQL migration via asyncpg
- Connection pooling configured (pool_size=10, max_overflow=20)

**Data Models**
- `User`: Tracks Telegram users with message counts
- `Group`: Stores group configurations (welcome messages, AutoMod settings, log channels, timezones)
- `GroupUser`: Many-to-many relationship for user-group associations
- `ModerationLog`: Audit trail for moderation actions
- `SpotifyTrack`: Stores music listening history for users in groups

### Module Architecture

The application follows a strict modular design with separation of concerns:

**Entry Point** (`main.py`)
- Minimal bootstrap that delegates to `src/bot.py`

**Core Bot** (`src/bot.py`)
- Initializes the Telegram Application
- Registers all module handlers
- Configures logging with security measures (httpx/telegram loggers set to WARNING to prevent token exposure)
- Provides `/start` command with formal help text
- Includes comprehensive `/ajuda` help system with all commands documented

**Module System** (`src/modules/`)
Each major feature is isolated in its own module:
- `moderation.py`: Admin commands (ban, kick, mute, nuke, purge)
- `automod.py`: Automatic filtering of links and spam
- `configuration.py`: Interactive settings menu with inline keyboards
- `rank.py`: Message tracking and ranking system
- `ai.py`: External API integrations for image generation, search, and chat
- `spotify_music.py`: Spotify integration for music tracking and statistics

**Utilities** (`src/utils/`)
- `permissions.py`: Permission checking logic (admin verification, bot capabilities)
- `responses.py`: Centralized formal response messages (no emojis, institutional tone)

**Database** (`src/database/`)
- `db.py`: Database connection manager with session factory
- `models.py`: SQLAlchemy declarative models

### Key Design Patterns

**Permission System**
- Dual-layer verification: user permissions AND bot permissions
- Prevents command execution if bot lacks required admin rights
- Reply-based command support (respond to a message instead of mentioning)

**Batch Processing for Scale**
- `/nuke` command processes messages in configurable batches (NUKE_BATCH_SIZE=100)
- Rate limiting with configurable delays (RATE_LIMIT_DELAY=0.5s)
- Designed to handle 10,000+ messages efficiently

**Configuration Management**
- Environment variables via python-dotenv
- Centralized config in `src/config.py`
- Type-safe with `typing.Final` annotations

**Error Handling**
- Graceful degradation when API keys are missing
- Formal error messages with correct syntax examples
- TelegramError exceptions caught and logged

**Response Style**
- All bot responses are strictly formal and professional
- No emojis or casual language
- Institutional tone as per requirements ("Procedimento de anulação de histórico concluído com êxito")

### Moderation Features

**Critical Commands**
- `/nuke`: Mass deletion without confirmation, processes entire chat history
- `/purge @user {count}`: Targeted message deletion

**Standard Moderation**
- Time-based muting with natural language parsing (e.g., "5 minutos", "1 hora")
- Ban/unban with optional reason tracking
- Kick for immediate removal

**AutoMod System**
- Configurable link filtering using regex
- Spam detection (placeholder for future enhancement)
- Excludes administrators from automatic moderation

### Rank System

- Passive message counting for all non-command messages
- Per-group ranking with position calculation
- Automatic user/group creation on first interaction

### Spotify Music Integration

**Overview**
Fui desenvolvido por: @vgsswon com propósito de interação com seu spotify! Para seus amigos escutar músicas que você escuta no dia a dia! Fornece rastreamento de música em tempo real, estatísticas, descoberta e recursos sociais. Cada membro conecta sua própria conta do Spotify pelo Telegram usando OAuth.

**Autenticação por Usuário**
- Cada membro conecta sua própria conta Spotify diretamente pelo bot
- Sistema OAuth individual com servidor dedicado na porta 5000
- Token refresh automático para cada usuário
- Armazenamento seguro no banco de dados (tabela `spotify_accounts`)
- Workflow separado: "Telegram Bot" (bot) e "OAuth Server" (autenticação)

**Comandos Principais**
- `.fm` - Mostra a música que o usuário está ouvindo agora com capa do álbum
- `.profile` - Perfil musical do usuário com estatísticas gerais
- `.chart [w/m/y]` - Gráficos das top músicas e artistas (semanal, mensal, anual/alltime)
- `.plays` - Histórico das últimas 10 reproduções
- `.w` - Estatísticas detalhadas das últimas 4 semanas

**Comandos Sociais**
- `.whoknows [artista]` - Top ouvintes de um artista no grupo (ranking)
- `.crowns` - Ranking de quem tem mais crowns (artistas dominados) no grupo
- `.friends` - Ver o que seus amigos estão ouvindo em tempo real
- `/adicionaramigo` - Adicionar amigo para acompanhar (responda mensagem ou mencione)

**Comandos de Pesquisa**
- `/pesquisarmusica {query}` - Buscar músicas no Spotify
- `/pesquisarartista {query}` - Buscar artistas com seguidores e gêneros
- `/pesquisaralbum {query}` - Buscar álbuns com data de lançamento

**Sistema de Crowns**
- Tabela `artist_crowns` armazena quem tem mais plays de cada artista por grupo
- Atualização automática ao usar `.whoknows`
- Constraint de unicidade (group_id, artist_name) garante um único dono por artista
- Exibição de 👑 para o top ouvinte no `.whoknows`

**Sistema de Amigos**
- Tabela `user_friends` com constraint de unicidade e verificação de auto-amizade
- Ver músicas que amigos estão ouvindo em tempo real
- Privacidade: apenas quem você adiciona como amigo

**Database Tracking**
- `spotify_tracks`: Histórico de músicas tocadas (salvo ao usar .fm)
- `spotify_accounts`: Tokens OAuth por usuário com refresh automático
- `artist_crowns`: Registro de quem domina cada artista por grupo
- `user_friends`: Lista de amizades para recurso .friends
- `user_settings`: Configurações personalizadas (futuro)

**Servidor OAuth**
- Arquivo `run_oauth.py` roda servidor Quart na porta 5000
- Endpoints: `/auth/spotify` (inicia OAuth), `/callback/spotify` (callback), `/health`
- Gera links únicos por usuário: `https://[seu-repl]/auth/spotify?user_id=[id]`
- Credenciais em secrets: `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`
- Redirect URI gerado automaticamente baseado em `REPLIT_DOMAINS`

## External Dependencies

### Required APIs

**Telegram Bot API**
- Primary interface via python-telegram-bot library
- Requires BOT_TOKEN environment variable
- Uses async methods for all interactions

**Database**
- SQLite with aiosqlite for async operations (default)
- Designed for PostgreSQL with asyncpg driver (DATABASE_URL configuration)

### Optional AI Services

**OpenAI API** (OPENAI_API_KEY)
- `/gerarimagem`: DALL-E 3 image generation (1024x1024)
- `/perguntar`: GPT-4 conversational AI (implementation pending)

**Google Custom Search** (GOOGLE_API_KEY, GOOGLE_CSE_ID)
- `/pesquisar`: Web search with snippet extraction

### Python Dependencies

**Core Libraries**
- python-telegram-bot 20.x+ (async bot framework)
- SQLAlchemy 2.0+ (async ORM)
- aiosqlite (async SQLite driver)
- python-dotenv (environment management)
- aiohttp (async HTTP client for external APIs)

**Prepared For**
- asyncpg (PostgreSQL async driver)
- Motor (MongoDB async ODM, if switching from SQL)

### Environment Configuration

Required variables:
- `BOT_TOKEN`: Telegram Bot API token

Optional variables:
- `OPENAI_API_KEY`: For AI features
- `GOOGLE_API_KEY`: For search functionality
- `GOOGLE_CSE_ID`: Google Custom Search Engine ID
- `DATABASE_URL`: Override default SQLite (e.g., PostgreSQL connection string)

### Database Migration Path

The current architecture uses SQLite for simplicity but is fully prepared for PostgreSQL:
- All database operations use async sessions
- Models are compatible with both SQLite and PostgreSQL
- Connection string configuration in `src/config.py`
- No code changes needed, only environment variable update