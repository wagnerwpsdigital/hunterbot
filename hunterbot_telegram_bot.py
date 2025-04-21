import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from scraper_modular import buscar_em_fontes

# 🔐 Insira seu token aqui
TOKEN = "SEU_TOKEN_DO_BOT_AQUI"

# Comando inicial
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Olá! Me envie o nome de um produto para eu buscar os menores preços para você."
    )

# Mensagens comuns (pesquisa de produtos)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text(f"🔎 Buscando por: {query}...")

    try:
        resultados, fontes = buscar_em_fontes(query)
        if resultados:
            for item in resultados:
                texto = (
                    f"📦 *{item['Produto']}*\n"
                    f"💰 R$ {item['Preço (R$)']:.2f}\n"
                    f"🏬 {item['Loja']}\n"
                    f"🔗 [Abrir Link]({item['Link']})"
                )
                await update.message.reply_markdown(texto)
        else:
            await update.message.reply_text("Nenhum resultado encontrado.")
    except Exception as e:
        await update.message.reply_text("⚠️ Erro ao buscar dados.")
        logging.error(e)

    await update.message.reply_text("✅ Busca concluída.\n" + "\n".join(fontes))

# Execução principal
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()# Telegram bot handler (resumo)
