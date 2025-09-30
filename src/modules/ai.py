"""
Módulo de IA - Geração de imagem, pesquisa e chat
"""
import aiohttp
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from src.config import OPENAI_API_KEY, GOOGLE_API_KEY, GOOGLE_CSE_ID
from src.utils.responses import responses


async def generate_image_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /gerarimagem - Gera imagem usando IA"""
    if not update.message:
        return
    
    if not OPENAI_API_KEY:
        await update.message.reply_text(responses.API_KEY_MISSING)
        return
    
    if not context.args:
        await update.message.reply_text(
            responses.INVALID_SYNTAX.format(syntax="/gerarimagem {descrição da imagem}")
        )
        return
    
    prompt = " ".join(context.args)
    progress_msg = await update.message.reply_text(responses.IMAGE_GENERATING)
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024"
            }
            
            async with session.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json=data
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    image_url = result["data"][0]["url"]
                    
                    await progress_msg.delete()
                    await update.message.reply_photo(
                        photo=image_url,
                        caption=responses.IMAGE_SUCCESS
                    )
                else:
                    error_data = await resp.text()
                    await progress_msg.edit_text(f"{responses.IMAGE_ERROR}\n{error_data}")
    except Exception as e:
        await progress_msg.edit_text(f"{responses.IMAGE_ERROR}\n{str(e)}")


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /pesquisar - Pesquisa na web"""
    if not update.message:
        return
    
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        await update.message.reply_text(responses.API_KEY_MISSING)
        return
    
    if not context.args:
        await update.message.reply_text(
            responses.INVALID_SYNTAX.format(syntax="/pesquisar {consulta}")
        )
        return
    
    query = " ".join(context.args)
    progress_msg = await update.message.reply_text(responses.SEARCH_IN_PROGRESS)
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={query}"
            
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    if "items" in data and len(data["items"]) > 0:
                        result = data["items"][0]
                        title = result.get("title", "")
                        snippet = result.get("snippet", "")
                        link = result.get("link", "")
                        
                        response = f"Resultado da Pesquisa:\n\n{title}\n\n{snippet}\n\n{link}"
                        await progress_msg.edit_text(response)
                    else:
                        await progress_msg.edit_text("Nenhum resultado encontrado.")
                else:
                    await progress_msg.edit_text(responses.SEARCH_ERROR)
    except Exception as e:
        await progress_msg.edit_text(f"{responses.SEARCH_ERROR}\n{str(e)}")


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /perguntar - Chat com IA"""
    if not update.message:
        return
    
    if not OPENAI_API_KEY:
        await update.message.reply_text(responses.API_KEY_MISSING)
        return
    
    if not context.args:
        await update.message.reply_text(
            responses.INVALID_SYNTAX.format(syntax="/perguntar {pergunta}")
        )
        return
    
    question = " ".join(context.args)
    progress_msg = await update.message.reply_text(responses.AI_PROCESSING)
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "Você é um assistente formal e profissional. Responda de forma objetiva e informativa, sem usar emojis."
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                "max_tokens": 500
            }
            
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    answer = result["choices"][0]["message"]["content"]
                    
                    await progress_msg.edit_text(f"Resposta:\n\n{answer}")
                else:
                    error_data = await resp.text()
                    await progress_msg.edit_text(f"{responses.AI_ERROR}\n{error_data}")
    except Exception as e:
        await progress_msg.edit_text(f"{responses.AI_ERROR}\n{str(e)}")


def register_ai_handlers(application) -> None:
    """Registra handlers de IA"""
    application.add_handler(CommandHandler("gerarimagem", generate_image_command))
    application.add_handler(CommandHandler("pesquisar", search_command))
    application.add_handler(CommandHandler("perguntar", ask_command))
