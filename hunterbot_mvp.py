import streamlit as st
import sqlite3
import pandas as pd
from scraper_modular import buscar_em_fontes
from datetime import datetime

st.set_page_config(page_title="HunterBot MVP", layout="wide")

# Conexão com SQLite
conn = sqlite3.connect("hunterbot_memoria.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    termo TEXT,
    preco_min REAL,
    preco_max REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS aprendizado (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    termo TEXT,
    origem TEXT,
    confiavel BOOLEAN,
    preco REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)''')
conn.commit()

# Menu lateral
aba = st.sidebar.selectbox("Menu", ["Buscar Produtos", "Histórico", "Painel de Uso", "Aprendizado Inteligente"])

if aba == "Buscar Produtos":
    st.title("HunterBot MVP – Busca Inteligente de Produtos")
    termo = st.text_input("🔎 O que deseja buscar?", "Cafeteira Oster térmica")
    preco_min = st.number_input("Preço mínimo (R$)", min_value=0.0, value=0.0)
    preco_max = st.number_input("Preço máximo (R$)", min_value=0.0, value=1000.0)

    if st.button("Buscar Preços"):
        st.info("Buscando em múltiplas fontes... aguarde.")
        resultados, fontes = buscar_em_fontes(termo, minimo=10)
        resultados_filtrados = [r for r in resultados if preco_min <= r["Preço (R$)"] <= preco_max]

        cursor.execute("INSERT INTO historico (termo, preco_min, preco_max) VALUES (?, ?, ?)",
                       (termo, preco_min, preco_max))
        conn.commit()

        if resultados_filtrados:
            df = pd.DataFrame(resultados_filtrados)
            st.success(f"{len(df)} resultados encontrados!")
            st.dataframe(df)
            st.download_button("⬇ Baixar resultados", df.to_csv(index=False).encode('utf-8'), "resultados.csv")
        else:
            st.warning("Nenhum resultado dentro da faixa de preço. Exibindo todos:")
            df = pd.DataFrame(resultados)
            st.dataframe(df)
        st.markdown("**Fontes utilizadas:**\n" + "\n".join([f"- {f}" for f in fontes]))

elif aba == "Histórico":
    st.title("📜 Histórico de Pesquisas")
    df = pd.read_sql_query("SELECT * FROM historico ORDER BY timestamp DESC", conn)
    st.dataframe(df)
    st.download_button("⬇ Baixar histórico", df.to_csv(index=False).encode('utf-8'), "historico.csv")

elif aba == "Painel de Uso":
    st.title("📈 Painel de Tendências e Comportamento")
    df = pd.read_sql_query("SELECT * FROM historico", conn)
    if df.empty:
        st.warning("Nenhuma pesquisa registrada ainda.")
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["Data"] = df["timestamp"].dt.date
        st.subheader("🔝 Termos mais buscados")
        st.bar_chart(df["termo"].value_counts().head(10))

        st.subheader("📅 Volume diário de buscas")
        st.line_chart(df.groupby("Data").size())

        st.subheader("💰 Faixas de preço mais usadas")
        st.line_chart(df[["preco_min", "preco_max"]])

elif aba == "Aprendizado Inteligente":
    st.title("🧠 Painel de Aprendizado da Ferramenta")
    df_aprend = pd.read_sql_query("SELECT * FROM aprendizado", conn)
    if df_aprend.empty:
        st.warning("Ainda não há dados de aprendizado registrados.")
    else:
        df_aprend["timestamp"] = pd.to_datetime(df_aprend["timestamp"])
        df_aprend["Data"] = df_aprend["timestamp"].dt.date

        st.subheader("📊 Termos mais registrados")
        st.bar_chart(df_aprend["termo"].value_counts().head(10))

        st.subheader("📍 Origem das informações")
        st.bar_chart(df_aprend["origem"].value_counts())

        st.subheader("📈 Preços por tipo de fonte")
        confiaveis = df_aprend[df_aprend["confiavel"] == 1]
        nao_confiaveis = df_aprend[df_aprend["confiavel"] == 0]

        st.write("**Preço médio - Fontes confiáveis**")
        st.metric("Preço Médio (R$)", f"{confiaveis['preco'].mean():.2f}")

        st.write("**Preço médio - Fontes não confiáveis**")
        st.metric("Preço Médio (R$)", f"{nao_confiaveis['preco'].mean():.2f}")

        st.subheader("🗂️ Todos os registros de aprendizado")
        st.dataframe(df_aprend)
        st.download_button("⬇ Baixar base de aprendizado", df_aprend.to_csv(index=False).encode('utf-8'), "aprendizado.csv")
