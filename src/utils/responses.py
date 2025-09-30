"""
Respostas formais do bot
"""


class FormalResponses:
    """Classe com todas as respostas formais do bot"""
    
    # Erros de permissão
    NO_PERMISSION = "Acesso negado. Você não possui as permissões necessárias para executar este comando."
    BOT_NO_PERMISSION = "Operação impossível. O bot não possui as permissões necessárias neste grupo."
    
    # Erros de sintaxe
    INVALID_SYNTAX = "Sintaxe inválida. Utilize: {syntax}"
    USER_NOT_FOUND = "Usuário não identificado. Mencione um usuário válido ou responda a uma mensagem."
    INVALID_DURATION = "Duração inválida. Formato aceito: número + unidade (ex: 5 minutos, 1 hora, 30 segundos)."
    
    # Sucesso - Moderação
    BAN_SUCCESS = "Usuário {user} banido permanentemente do grupo."
    KICK_SUCCESS = "Usuário {user} removido do grupo."
    MUTE_SUCCESS = "Usuário {user} silenciado."
    MUTE_TIMED_SUCCESS = "Usuário {user} silenciado por {duration}."
    UNMUTE_SUCCESS = "Restrições de {user} removidas com êxito."
    UNBAN_SUCCESS = "Banimento de {user} revogado."
    
    # Nuke e Purge
    NUKE_SUCCESS = "Procedimento de anulação de histórico concluído com êxito."
    NUKE_IN_PROGRESS = "Iniciando procedimento de anulação de histórico. Aguarde."
    PURGE_SUCCESS = "Remoção de {count} mensagens do usuário {user} finalizada."
    PURGE_IN_PROGRESS = "Processando remoção de mensagens. Aguarde."
    
    # Rank
    RANK_MESSAGE = "Posição no ranking: #{position}\nTotal de mensagens: {count}"
    RANK_NOT_FOUND = "Registro não encontrado. Você ainda não enviou mensagens neste grupo."
    
    # Configurações
    CONFIG_WELCOME = "Configurações de boas-vindas atualizadas."
    CONFIG_AUTOMOD = "Configurações de moderação automática atualizadas."
    CONFIG_LOG = "Canal de registro atualizado."
    CONFIG_TIMEZONE = "Fuso horário atualizado para: {timezone}"
    
    # AI Features
    IMAGE_GENERATING = "Processando solicitação de geração de imagem. Aguarde."
    IMAGE_SUCCESS = "Imagem gerada com êxito."
    IMAGE_ERROR = "Falha ao gerar imagem. Verifique os parâmetros ou tente novamente."
    
    SEARCH_IN_PROGRESS = "Executando pesquisa. Aguarde."
    SEARCH_ERROR = "Falha na operação de pesquisa. Tente novamente."
    
    AI_PROCESSING = "Processando consulta. Aguarde."
    AI_ERROR = "Falha ao processar consulta. Verifique a configuração da API."
    
    # API Keys não configuradas
    API_KEY_MISSING = "Operação indisponível. A chave de API necessária não foi configurada."
    
    # AutoMod
    LINK_DETECTED = "Link não autorizado detectado e removido."
    SPAM_DETECTED = "Conteúdo identificado como spam e removido."
    
    # Errors gerais
    OPERATION_FAILED = "Falha operacional detectada. Verifique a sintaxe ou suas permissões."
    DATABASE_ERROR = "Erro interno no sistema de banco de dados."


responses = FormalResponses()
