# hunterbot_telegram_bot.py
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
import sqlite3
import pandas as pd
from scraper_modular import search_mercado_livre, search_fake_sources
import matplotlib.pyplot as plt
import io
import time
from db_connector import salvar_dataframe, ler_tabela

# Exemplo: salvar uma pesquisa no histórico
df_novo = pd.DataFrame([{
    "termo": termo,
    "preco_min": preco_min,
    "preco_max": preco_max
}])
salvar_dataframe(df_novo, "historico")
# Carregar variáveis de ambiente de um arquivo .env
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token do bot Telegram - deve ser obtido com o BotFather
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN não encontrado no arquivo .env")

# Conectar ao mesmo banco de dados do app principal
def get_db_connection():
    return sqlite3.connect('hunterbot.db')

# Comandos do bot
async def start(update: Update, context: CallbackContext) -> None:
    """Envia uma mensagem quando o comando /start é emitido."""
    user = update.effective_user
    await update.message.reply_text(
        f'Olá, {user.first_name}! 🔍\n\n'
        f'Eu sou o HunterBot, seu agente de inteligência digital automatizado.\n\n'
        f'Use o comando /buscar seguido do que deseja procurar.\n'
        f'Exemplo: /buscar smartphone\n\n'
        f'Outros comandos:\n'
        f'/ajuda - Mostra esta mensagem de ajuda\n'
        f'/estatisticas - Exibe estatísticas das suas buscas\n'
        f'/historico - Mostra suas últimas buscas'
    )

async def help_command(update: Update, context: CallbackContext) -> None:
    """Envia uma mensagem quando o comando /ajuda é emitido."""
    await update.message.reply_text(
        '🔍 *HunterBot - Comandos Disponíveis*\n\n'
        '*Comandos básicos:*\n'
        '/buscar [termo] - Busca produtos ou serviços\n'
        '/buscar [termo] [min] [max] - Busca com filtro de preço\n'
        '/historico - Exibe suas últimas buscas\n'
        '/estatisticas - Mostra gráficos e insights\n'
        '/ajuda - Exibe esta mensagem\n\n'
        '*Exemplos:*\n'
        '/buscar smartphone\n'
        '/buscar notebook 2000 5000\n',
        parse_mode='Markdown'
    )

async def search_command(update: Update, context: CallbackContext) -> None:
    """Processa o comando /buscar."""
    args = context.args
    
    if not args:
        await update.message.reply_text('Por favor, informe o que deseja buscar.\nExemplo: /buscar smartphone')
        return
    
    # Extrair termo de busca e filtros de preço (opcionais)
    search_term = args[0]
    min_price = 0.0
    max_price = float('inf')
    
    # Verificar se há filtros de preço
    if len(args) >= 3:
        try:
            min_price = float(args[1])
            max_price = float(args[2])
        except ValueError:
            # Se não for possível converter para float, assume que tudo é parte do termo de busca
            search_term = ' '.join(args)
    elif len(args) > 1:
        # Se só houver dois argumentos ou não for possível converter para float
        search_term = ' '.join(args)
    
    # Mensagem de processamento
    processing_msg = await update.message.reply_text(
        f'🔍 Buscando por "{search_term}"...\n'
        f'Aguarde um momento, estou vasculhando várias fontes.'
    )
    
    # Buscar resultados
    try:
        # Buscar em fontes confiáveis
        trusted_results = search_mercado_livre(search_term, min_price, max_price)
        trusted_results = trusted_results[:5]  # Limitar a 5 resultados
        
        # Buscar em fontes não confiáveis (simuladas)
        untrusted_results = search_fake_sources(search_term, min_price, max_price)
        untrusted_results = untrusted_results[:5]  # Limitar a 5 resultados
        
        # Combinar resultados
        all_results = trusted_results + untrusted_results
        
        # Salvar no banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Salvar pesquisa
        cursor.execute('''
        INSERT INTO searches (search_term, min_price, max_price)
        VALUES (?, ?, ?)
        ''', (search_term, min_price, max_price if max_price != float('inf') else None))
        
        search_id = cursor.lastrowid
        
        # Salvar resultados
        for result in all_results:
            cursor.execute('''
            INSERT INTO search_results (search_id, title, price, url, source, is_trusted)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (search_id, result['title'], result['price'], result['url'], result['source'], result['is_trusted']))
        
        # Atualizar dados de aprendizado
        for result in all_results:
            # Verificar se já existe registro para este termo e fonte
            cursor.execute('''
            SELECT * FROM learning_data 
            WHERE search_term = ? AND source = ? AND is_trusted = ?
            ''', (search_term, result['source'], result['is_trusted']))
            
            existing = cursor.fetchone()
            
            if existing:
                # Atualizar registro existente
                cursor.execute('''
                UPDATE learning_data
                SET avg_price = (avg_price * search_count + ?) / (search_count + 1),
                    search_count = search_count + 1,
                    last_updated = CURRENT_TIMESTAMP
                WHERE search_term = ? AND source = ? AND is_trusted = ?
                ''', (result['price'], search_term, result['source'], result['is_trusted']))
            else:
                # Criar novo registro
                cursor.execute('''
                INSERT INTO learning_data (search_term, source, is_trusted, avg_price)
                VALUES (?, ?, ?, ?)
                ''', (search_term, result['source'], result['is_trusted'], result['price']))
        
        conn.commit()
        conn.close()
        
        # Formatar resultados para resposta
        response = f'🔍 *Resultados para "{search_term}"*\n'
        
        if trusted_results:
            response += '\n*Fontes Confiáveis:*\n'
            for i, result in enumerate(trusted_results[:3], 1):  # Mostrar apenas os 3 primeiros para não sobrecarregar
                response += f"{i}. [{result['title']}]({result['url']})\n" \
                          f"   💰 R$ {result['price']:.2f} - {result['source']}\n\n"
            
            if len(trusted_results) > 3:
                response += f"_...e mais {len(trusted_results) - 3} resultados de fontes confiáveis._\n"
        else:
            response += '\n*Fontes Confiáveis:* Nenhum resultado encontrado.\n'
        
        if untrusted_results:
            response += '\n*Fontes Não Confiáveis:* ⚠️\n'
            for i, result in enumerate(untrusted_results[:3], 1):  # Mostrar apenas os 3 primeiros
                response += f"{i}. [{result['title']}]({result['url']})\n" \
                          f"   💰 R$ {result['price']:.2f} - {result['source']}\n\n"
            
            if len(untrusted_results) > 3:
                response += f"_...e mais {len(untrusted_results) - 3} resultados de fontes não confiáveis._\n"
        else:
            response += '\n*Fontes Não Confiáveis:* Nenhum resultado encontrado.\n'
        
        response += '\nPara ver mais detalhes, acesse o nosso painel web ou use o comando /estatisticas.'
        
        # Remover mensagem de processamento e enviar resultados
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_msg.message_id)
        await update.message.reply_text(response, parse_mode='Markdown', disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=processing_msg.message_id)
        await update.message.reply_text(f"❌ Ocorreu um erro ao processar sua busca. Por favor, tente novamente.")

async def history_command(update: Update, context: CallbackContext) -> None:
    """Exibe o histórico de buscas recentes."""
    try:
        conn = get_db_connection()
        search_history = pd.read_sql_query('''
        SELECT s.id, s.search_term, s.timestamp, s.min_price, s.max_price,
               COUNT(sr.id) as result_count,
               AVG(CASE WHEN sr.is_trusted = 1 THEN sr.price ELSE NULL END) as avg_trusted_price,
               AVG(CASE WHEN sr.is_trusted = 0 THEN sr.price ELSE NULL END) as avg_untrusted_price
        FROM searches s
        LEFT JOIN search_results sr ON s.id = sr.search_id
        GROUP BY s.id
        ORDER BY s.timestamp DESC
        LIMIT 10
        ''', conn)
        conn.close()
        
        if search_history.empty:
            await update.message.reply_text('Nenhuma busca realizada ainda.')
            return
        
        # Formatar resposta
        response = '*📚 Histórico de Buscas Recentes*\n\n'
        
        for _, row in search_history.iterrows():
            timestamp = pd.to_datetime(row['timestamp'])
            date_str = timestamp.strftime('%d/%m/%Y %H:%M')
            
            response += f"• *{row['search_term']}*\n"
            response += f"  📅 {date_str}\n"
            
            min_price = row['min_price']
            max_price = row['max_price']
            if pd.notnull(min_price) and pd.notnull(max_price):
                response += f"  💰 Preço: R$ {min_price:.2f} - R$ {max_price:.2f}\n"
            
            response += f"  🔍 {row['result_count']} resultados\n\n"
        
        response += "Use /buscar [termo] para realizar uma nova busca."
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {e}")
        await update.message.reply_text("❌ Ocorreu um erro ao buscar o histórico. Por favor, tente novamente.")

async def stats_command(update: Update, context: CallbackContext) -> None:
    """Exibe estatísticas e insights."""
    try:
        conn = get_db_connection()
        
        # Top termos buscados
        top_terms = pd.read_sql_query('''
        SELECT search_term, COUNT(*) as count
        FROM searches
        GROUP BY search_term
        ORDER BY count DESC
        LIMIT 5
        ''', conn)
        
        # Diferença média de preço
        price_diff = pd.read_sql_query('''
        SELECT ld.search_term,
               AVG(CASE WHEN ld.is_trusted = 1 THEN ld.avg_price ELSE NULL END) as trusted_avg,
               AVG(CASE WHEN ld.is_trusted = 0 THEN ld.avg_price ELSE NULL END) as untrusted_avg
        FROM learning_data ld
        GROUP BY ld.search_term
        HAVING trusted_avg IS NOT NULL AND untrusted_avg IS NOT NULL
        ORDER BY ABS(trusted_avg - untrusted_avg) DESC
        LIMIT 5
        ''', conn)
        
        conn.close()
        
        if top_terms.empty:
            await update.message.reply_text('Ainda não há dados suficientes para gerar estatísticas.')
            return
        
        # Gerar um gráfico com os termos mais buscados
        plt.figure(figsize=(10, 6))
        
        # Criar o gráfico
        plt.bar(top_terms['search_term'], top_terms['count'], color='skyblue')
        plt.title('Termos Mais Buscados')
        plt.xlabel('Termo')
        plt.ylabel('Número de Buscas')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Salvar em um buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Enviar o gráfico
        await update.message.reply_photo(
            photo=buf,
            caption='📊 *Top 5 Termos Mais Buscados*',
            parse_mode='Markdown'
        )
        
        # Preparar insights de texto
        insights = '*🧠 Insights do HunterBot*\n\n'
        
        # Insights sobre diferença de preço
        if not price_diff.empty:
            insights += '*Diferença de Preço entre Fontes:*\n'
            
            for _, row in price_diff.iterrows():
                term = row['search_term']
                trusted = row['trusted_avg']
                untrusted = row['untrusted_avg']
                
                if pd.notnull(trusted) and pd.notnull(untrusted):
                    diff_pct = abs((trusted - untrusted) / trusted * 100) if trusted > 0 else 0
                    
                    if trusted > untrusted:
                        insights += f"• *{term}*: Fontes não confiáveis são {diff_pct:.1f}% mais baratas\n"
                    else:
                        insights += f"• *{term}*: Fontes confiáveis são {diff_pct:.1f}% mais baratas\n"
        
        # Adicionar recomendações
        insights += '\n*Recomendações:*\n'
        insights += '• Verifique sempre a confiabilidade das fontes antes de realizar uma compra.\n'
        insights += '• Compare os preços entre diferentes tipos de fontes para obter a melhor oferta.\n'
        insights += '• Utilize termos de busca mais específicos para resultados mais relevantes.\n'
        
        # Enviar os insights
        await update.message.reply_text(insights, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Erro ao gerar estatísticas: {e}")
        await update.message.reply_text("❌ Ocorreu um erro ao gerar estatísticas. Por favor, tente novamente.")

async def unknown_command(update: Update, context: CallbackContext) -> None:
    """Responde a comandos desconhecidos."""
    await update.message.reply_text(
        'Comando não reconhecido. Use /ajuda para ver os comandos disponíveis.'
    )

async def message_handler(update: Update, context: CallbackContext) -> None:
    """Lida com mensagens normais (não comandos)."""
    text = update.message.text
    
    # Assumir que mensagens sem comando são termos de busca
    context.args = text.split()
    await search_command(update, context)

def main() -> None:
    """Inicia o bot."""
    # Criar o aplicativo
    application = Application.builder().token(TOKEN).build()
    
    # Adicionar handlers para comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ajuda", help_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("buscar", search_command))
    application.add_handler(CommandHandler("historico", history_command))
    application.add_handler(CommandHandler("estatisticas", stats_command))
    
    # Adicionar handlers para mensagens normais
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Handler para comandos desconhecidos
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    # Iniciar o bot
    logger.info("Bot iniciado. Pressione Ctrl+C para parar.")
    application.run_polling()

if __name__ == '__main__':
    main()
