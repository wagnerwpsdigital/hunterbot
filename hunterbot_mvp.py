# hunterbot_mvp.py
import streamlit as st, st.set_page_config(
    page_title="HunterBot - Agente de Inteligência Digital",
    layout="wide",
    initial_sidebar_state="expanded"
)
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import os
import random
from scraper_modular import buscar_em_fontes
from auth import login, registrar
st.sidebar.title("🔐 Login / Registro")
modo = st.sidebar.radio("Acesso", ["Login", "Registrar"])
email = st.sidebar.text_input("E-mail")
senha = st.sidebar.text_input("Senha", type="password")
if modo == "Login":
    if st.sidebar.button("Entrar"):
        result = login(email, senha)
        if result.user:
            st.session_state["usuario_logado"] = result.user.email
            st.success(f"Bem-vindo, {result.user.email}")
        else:
            st.error("Login inválido")
elif modo == "Registrar":
    if st.sidebar.button("Criar conta"):
        result = registrar(email, senha)
        if result.user:
            st.success("Conta criada. Faça login agora.")
        else:
            st.error("Erro ao registrar")
# Funções substitutas temporárias
def search_mercado_livre(query, min_price=None, max_price=None):
    return []  # Retorna lista vazia temporariamente
    
def search_fake_sources(query, min_price=None, max_price=None):
    return []  # Retorna lista vazia temporariamente
# Configuração da página
st.set_page_config(
    page_title="HunterBot - Agente de Inteligência Digital",
    page_icon="🔍",
    layout="wide",
)
# Inicialização do banco de dados
def init_db():
    conn = sqlite3.connect('hunterbot.db')
    c = conn.cursor()   
    # Tabela de pesquisas
    c.execute('''
    CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        search_term TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        min_price REAL,
        max_price REAL
    )
    ''')
    
    # Tabela de resultados
    c.execute('''
    CREATE TABLE IF NOT EXISTS search_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        search_id INTEGER,
        title TEXT NOT NULL,
        price REAL,
        url TEXT,
        source TEXT,
        is_trusted BOOLEAN,
        FOREIGN KEY (search_id) REFERENCES searches(id)
    )
    ''')
    
    # Tabela de aprendizado
    c.execute('''
    CREATE TABLE IF NOT EXISTS learning_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        search_term TEXT NOT NULL,
        source TEXT,
        is_trusted BOOLEAN,
        avg_price REAL,
        search_count INTEGER DEFAULT 1,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

# Função para salvar busca e resultados no banco de dados
def save_search_results(search_term, min_price, max_price, results):
    conn = sqlite3.connect('hunterbot.db')
    c = conn.cursor()
    
    # Salvar pesquisa
    c.execute('''
    INSERT INTO searches (search_term, min_price, max_price)
    VALUES (?, ?, ?)
    ''', (search_term, min_price, max_price))
    
    search_id = c.lastrowid
    
    # Salvar resultados
    for result in results:
        c.execute('''
        INSERT INTO search_results (search_id, title, price, url, source, is_trusted)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (search_id, result['title'], result['price'], result['url'], result['source'], result['is_trusted']))
    
    # Atualizar dados de aprendizado
    for result in results:
        # Verificar se já existe registro para este termo e fonte
        c.execute('''
        SELECT * FROM learning_data 
        WHERE search_term = ? AND source = ? AND is_trusted = ?
        ''', (search_term, result['source'], result['is_trusted']))
        
        existing = c.fetchone()
        
        if existing:
            # Atualizar registro existente
            c.execute('''
            UPDATE learning_data
            SET avg_price = (avg_price * search_count + ?) / (search_count + 1),
                search_count = search_count + 1,
                last_updated = CURRENT_TIMESTAMP
            WHERE search_term = ? AND source = ? AND is_trusted = ?
            ''', (result['price'], search_term, result['source'], result['is_trusted']))
        else:
            # Criar novo registro
            c.execute('''
            INSERT INTO learning_data (search_term, source, is_trusted, avg_price)
            VALUES (?, ?, ?, ?)
            ''', (search_term, result['source'], result['is_trusted'], result['price']))
    
    conn.commit()
    conn.close()

# Função para obter histórico de pesquisas
def get_search_history():
    conn = sqlite3.connect('hunterbot.db')
    search_history = pd.read_sql_query('''
    SELECT s.id, s.search_term, s.timestamp, s.min_price, s.max_price,
           COUNT(sr.id) as result_count,
           AVG(CASE WHEN sr.is_trusted = 1 THEN sr.price ELSE NULL END) as avg_trusted_price,
           AVG(CASE WHEN sr.is_trusted = 0 THEN sr.price ELSE NULL END) as avg_untrusted_price
    FROM searches s
    LEFT JOIN search_results sr ON s.id = sr.search_id
    GROUP BY s.id
    ORDER BY s.timestamp DESC
    LIMIT 100
    ''', conn)
    conn.close()
    return search_history

# Função para obter dados de aprendizado
def get_learning_data():
    conn = sqlite3.connect('hunterbot.db')
    learning_data = pd.read_sql_query('''
    SELECT search_term, source, is_trusted, avg_price, search_count, last_updated
    FROM learning_data
    ORDER BY search_count DESC, last_updated DESC
    ''', conn)
    conn.close()
    return learning_data

# Função para buscar resultados de uma pesquisa específica
def get_search_results(search_id):
    conn = sqlite3.connect('hunterbot.db')
    results = pd.read_sql_query('''
    SELECT sr.*, s.search_term
    FROM search_results sr
    JOIN searches s ON sr.search_id = s.id
    WHERE sr.search_id = ?
    ORDER BY sr.is_trusted DESC, sr.price ASC
    ''', conn, params=(search_id,))
    conn.close()
    return results

# Função para obter insights
def get_insights():
    conn = sqlite3.connect('hunterbot.db')
    c = conn.cursor()
    
    # Top termos buscados
    top_terms = pd.read_sql_query('''
    SELECT search_term, COUNT(*) as count
    FROM searches
    GROUP BY search_term
    ORDER BY count DESC
    LIMIT 10
    ''', conn)
    
    # Diferença média de preço entre fontes confiáveis e não confiáveis
    price_diff = pd.read_sql_query('''
    SELECT ld.search_term,
           AVG(CASE WHEN ld.is_trusted = 1 THEN ld.avg_price ELSE NULL END) as trusted_avg,
           AVG(CASE WHEN ld.is_trusted = 0 THEN ld.avg_price ELSE NULL END) as untrusted_avg,
           (AVG(CASE WHEN ld.is_trusted = 1 THEN ld.avg_price ELSE NULL END) - 
            AVG(CASE WHEN ld.is_trusted = 0 THEN ld.avg_price ELSE NULL END)) as price_diff
    FROM learning_data ld
    GROUP BY ld.search_term
    HAVING trusted_avg IS NOT NULL AND untrusted_avg IS NOT NULL
    ORDER BY ABS(price_diff) DESC
    LIMIT 10
    ''', conn)
    
    # Buscas por dia
    searches_by_day = pd.read_sql_query('''
    SELECT date(timestamp) as date, COUNT(*) as count
    FROM searches
    GROUP BY date(timestamp)
    ORDER BY date DESC
    LIMIT 30
    ''', conn)
    
    conn.close()
    return top_terms, price_diff, searches_by_day

# Inicializar o banco de dados
init_db()

# Título do aplicativo
st.title("🔍 HunterBot - Agente de Inteligência Digital")

# Sidebar para filtros e opções
st.sidebar.header("Configurações de Busca")

# Interface de pesquisa
search_term = st.sidebar.text_input("Termo de busca:")
min_price = st.sidebar.number_input("Preço mínimo:", min_value=0.0, value=0.0, step=10.0)
max_price = st.sidebar.number_input("Preço máximo:", min_value=0.0, value=10000.0, step=100.0)

if st.sidebar.button("Buscar"):
    if search_term:
        st.info(f"Buscando por '{search_term}' (Preço: R${min_price:.2f} - R${max_price:.2f})...")
        
        # Buscar em fontes confiáveis
        try:
            trusted_results = search_mercado_livre(search_term, min_price, max_price)
            # Limitar a 5 resultados
            trusted_results = trusted_results[:5]
        except Exception as e:
            st.error(f"Erro ao buscar em fontes confiáveis: {e}")
            trusted_results = []
        
        # Buscar em fontes não confiáveis (simuladas)
        try:
            untrusted_results = search_fake_sources(search_term, min_price, max_price)
            # Limitar a 5 resultados
            untrusted_results = untrusted_results[:5]
        except Exception as e:
            st.error(f"Erro ao buscar em fontes não confiáveis: {e}")
            untrusted_results = []
        
        # Combinar resultados
        all_results = trusted_results + untrusted_results
        
        # Salvar no banco de dados
        save_search_results(search_term, min_price, max_price, all_results)
        
        # Mostrar resultados
        st.success(f"Encontrados {len(all_results)} resultados.")
        
        # Interface com tabs para separar fontes confiáveis e não confiáveis
        tab1, tab2 = st.tabs(["Fontes Confiáveis", "Fontes Não Confiáveis/Simuladas"])
        
        with tab1:
            if trusted_results:
                st.subheader(f"Resultados de Fontes Confiáveis ({len(trusted_results)})")
                for i, result in enumerate(trusted_results):
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.write(f"**{result['title']}**")
                            st.write(f"Fonte: {result['source']}")
                        with col2:
                            st.write(f"**R$ {result['price']:.2f}**")
                        with col3:
                            st.write(f"[Ver Produto]({result['url']})")
                        st.divider()
            else:
                st.write("Nenhum resultado de fontes confiáveis encontrado.")
        
        with tab2:
            if untrusted_results:
                st.subheader(f"Resultados de Fontes Não Confiáveis ({len(untrusted_results)})")
                st.warning("⚠️ Esses resultados são de fontes não verificadas ou simuladas.")
                for i, result in enumerate(untrusted_results):
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.write(f"**{result['title']}**")
                            st.write(f"Fonte: {result['source']}")
                        with col2:
                            st.write(f"**R$ {result['price']:.2f}**")
                        with col3:
                            st.write(f"[Ver Produto]({result['url']})")
                        st.divider()
            else:
                st.write("Nenhum resultado de fontes não confiáveis encontrado.")
    else:
        st.error("Por favor, digite um termo de busca.")

# Interface com abas para resultados, histórico e insights
tab1, tab2, tab3 = st.tabs(["Painel", "Histórico de Pesquisas", "Aprendizado Inteligente"])

with tab1:
    st.header("Painel de Análise")
    
    # Obter dados para insights
    top_terms, price_diff, searches_by_day = get_insights()
    
    # Layout com 3 colunas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Termos Mais Buscados")
        if not top_terms.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='count', y='search_term', data=top_terms, ax=ax)
            ax.set_title('Top 10 Termos Buscados')
            ax.set_xlabel('Número de Buscas')
            ax.set_ylabel('Termo')
            st.pyplot(fig)
        else:
            st.write("Nenhum dado disponível ainda.")
    
    with col2:
        st.subheader("Buscas por Dia")
        if not searches_by_day.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.lineplot(x='date', y='count', data=searches_by_day, marker='o', ax=ax)
            ax.set_title('Buscas por Dia')
            ax.set_xlabel('Data')
            ax.set_ylabel('Número de Buscas')
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.write("Nenhum dado disponível ainda.")
    
    st.subheader("Diferença de Preço entre Fontes")
    if not price_diff.empty:
        # Formatar para exibição
        display_df = price_diff.copy()
        display_df['trusted_avg'] = display_df['trusted_avg'].apply(lambda x: f"R$ {x:.2f}" if pd.notnull(x) else "N/A")
        display_df['untrusted_avg'] = display_df['untrusted_avg'].apply(lambda x: f"R$ {x:.2f}" if pd.notnull(x) else "N/A")
        display_df['price_diff'] = display_df['price_diff'].apply(lambda x: f"R$ {x:.2f}" if pd.notnull(x) else "N/A")
        
        st.dataframe(
            display_df.rename(columns={
                'search_term': 'Termo de Busca',
                'trusted_avg': 'Média (Fontes Confiáveis)',
                'untrusted_avg': 'Média (Fontes Não Confiáveis)',
                'price_diff': 'Diferença'
            }),
            column_config={
                "Termo de Busca": st.column_config.TextColumn("Termo de Busca"),
                "Média (Fontes Confiáveis)": st.column_config.TextColumn("Média (Fontes Confiáveis)"),
                "Média (Fontes Não Confiáveis)": st.column_config.TextColumn("Média (Fontes Não Confiáveis)"),
                "Diferença": st.column_config.TextColumn("Diferença"),
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.write("Nenhum dado disponível ainda.")

with tab2:
    st.header("Histórico de Pesquisas")
    search_history = get_search_history()
    
    if not search_history.empty:
        # Formatar para exibição
        search_history['timestamp'] = pd.to_datetime(search_history['timestamp'])
        search_history['date'] = search_history['timestamp'].dt.strftime('%d/%m/%Y %H:%M')
        
        # Formatar preços
        search_history['min_price'] = search_history['min_price'].apply(lambda x: f"R$ {x:.2f}" if pd.notnull(x) else "N/A")
        search_history['max_price'] = search_history['max_price'].apply(lambda x: f"R$ {x:.2f}" if pd.notnull(x) else "N/A")
        search_history['avg_trusted_price'] = search_history['avg_trusted_price'].apply(lambda x: f"R$ {x:.2f}" if pd.notnull(x) else "N/A")
        search_history['avg_untrusted_price'] = search_history['avg_untrusted_price'].apply(lambda x: f"R$ {x:.2f}" if pd.notnull(x) else "N/A")
        
        # Display como tabela interativa
        selected_search = st.dataframe(
            search_history[[
                'search_term', 'date', 'min_price', 'max_price', 
                'result_count', 'avg_trusted_price', 'avg_untrusted_price'
            ]].rename(columns={
                'search_term': 'Termo de Busca',
                'date': 'Data/Hora',
                'min_price': 'Preço Mínimo',
                'max_price': 'Preço Máximo',
                'result_count': 'Resultados',
                'avg_trusted_price': 'Média (Fontes Confiáveis)',
                'avg_untrusted_price': 'Média (Fontes Não Confiáveis)'
            }),
            hide_index=True,
            use_container_width=True
        )
        
        # Ver detalhes de uma pesquisa específica
        search_id_to_view = st.selectbox(
            "Ver detalhes da pesquisa:",
            options=search_history['id'].tolist(),
            format_func=lambda x: f"ID {x}: {search_history[search_history['id'] == x]['search_term'].iloc[0]} ({search_history[search_history['id'] == x]['date'].iloc[0]})"
        )
        
        if search_id_to_view:
            search_results = get_search_results(search_id_to_view)
            
            if not search_results.empty:
                st.subheader(f"Resultados para '{search_results['search_term'].iloc[0]}'")
                
                # Formatar para exibição
                search_results['price'] = search_results['price'].apply(lambda x: f"R$ {x:.2f}")
                search_results['is_trusted'] = search_results['is_trusted'].apply(lambda x: "Confiável" if x else "Não Confiável")
                
                st.dataframe(
                    search_results[[
                        'title', 'price', 'source', 'is_trusted', 'url'
                    ]].rename(columns={
                        'title': 'Título',
                        'price': 'Preço',
                        'source': 'Fonte',
                        'is_trusted': 'Tipo de Fonte',
                        'url': 'URL'
                    }),
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "URL": st.column_config.LinkColumn("URL")
                    }
                )
            else:
                st.write("Nenhum resultado encontrado para esta pesquisa.")
    else:
        st.write("Nenhuma pesquisa realizada ainda.")

with tab3:
    st.header("Aprendizado Inteligente")
    learning_data = get_learning_data()
    
    if not learning_data.empty:
        st.subheader("Dados de Aprendizado")
        
        # Formatar para exibição
        learning_data['last_updated'] = pd.to_datetime(learning_data['last_updated'])
        learning_data['last_updated'] = learning_data['last_updated'].dt.strftime('%d/%m/%Y %H:%M')
        learning_data['is_trusted'] = learning_data['is_trusted'].apply(lambda x: "Confiável" if x else "Não Confiável")
        learning_data['avg_price'] = learning_data['avg_price'].apply(lambda x: f"R$ {x:.2f}")
        
        st.dataframe(
            learning_data.rename(columns={
                'search_term': 'Termo de Busca',
                'source': 'Fonte',
                'is_trusted': 'Tipo de Fonte',
                'avg_price': 'Preço Médio',
                'search_count': 'Total de Buscas',
                'last_updated': 'Última Atualização'
            }),
            hide_index=True,
            use_container_width=True
        )
        
        # Mostrar insights baseados nos dados de aprendizado
        st.subheader("Insights")
        
        # Agrupar dados por termo de busca e tipo de fonte
        if not learning_data.empty:
            insights = []
            
            # Termos mais buscados
            top_searched = learning_data.groupby('search_term')['search_count'].sum().sort_values(descending=True).head(3)
            if not top_searched.empty:
                top_terms = ", ".join([f"'{term}' ({count} buscas)" for term, count in top_searched.items()])
                insights.append(f"📈 Os termos mais buscados são {top_terms}.")
            
            # Fontes mais comuns
            top_sources = learning_data.groupby('source')['search_count'].sum().sort_values(descending=True).head(3)
            if not top_sources.empty:
                sources_list = ", ".join([f"'{source}' ({count} resultados)" for source, count in top_sources.items()])
                insights.append(f"🔍 As fontes mais comuns são {sources_list}.")
            
            # Diferença de preço entre fontes confiáveis e não confiáveis
            learning_data_numeric = learning_data.copy()
            learning_data_numeric['avg_price'] = learning_data_numeric['avg_price'].str.replace('R$ ', '').str.replace(',', '.').astype(float)
            learning_data_numeric['is_trusted'] = learning_data_numeric['is_trusted'].apply(lambda x: True if x == "Confiável" else False)
            
            # Calcular a média de preços por tipo de fonte
            avg_by_trust = learning_data_numeric.groupby('is_trusted')['avg_price'].mean()
            if len(avg_by_trust) == 2:
                trusted_avg = avg_by_trust[True]
                untrusted_avg = avg_by_trust[False]
                diff_pct = abs((trusted_avg - untrusted_avg) / trusted_avg * 100) if trusted_avg > 0 else 0
                
                if trusted_avg > untrusted_avg:
                    insights.append(f"💰 Em média, produtos em fontes não confiáveis são {diff_pct:.1f}% mais baratos (R$ {trusted_avg:.2f} vs R$ {untrusted_avg:.2f}).")
                else:
                    insights.append(f"💰 Em média, produtos em fontes confiáveis são {diff_pct:.1f}% mais baratos (R$ {trusted_avg:.2f} vs R$ {untrusted_avg:.2f}).")
            
            # Mostrar insights
            if insights:
                for insight in insights:
                    st.info(insight)
                
                # Recomendações baseadas nos dados
                st.subheader("Recomendações")
                st.success("✅ Com base nos seus padrões de busca, recomendamos:")
                
                recommendations = [
                    "Verificar sempre a confiabilidade das fontes antes de realizar uma compra.",
                    "Comparar os preços entre fontes confiáveis e não confiáveis para obter a melhor oferta.",
                    "Utilizar termos de busca mais específicos para encontrar resultados mais relevantes."
                ]
                
                for rec in recommendations:
                    st.write(f"• {rec}")
            else:
                st.write("Ainda não há insights suficientes baseados nos dados atuais.")
    else:
        st.write("Nenhum dado de aprendizado disponível ainda.")

# Rodapé
st.divider()
st.write("© 2025 HunterBot - Agente de Inteligência Digital Automatizado")
