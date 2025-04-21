import requests
from bs4 import BeautifulSoup
import re
import time
import sqlite3

# Cabeçalho de navegação
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Conexão com o banco de aprendizado
conn = sqlite3.connect("hunterbot_memoria.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS aprendizado (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    termo TEXT,
    origem TEXT,
    confiavel BOOLEAN,
    preco REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)''')
conn.commit()

# Função para extrair número de preço
def extrair_preco(preco_str):
    preco_str = preco_str.replace(".", "").replace(",", ".")
    match = re.findall(r"\d+\.\d+", preco_str)
    return float(match[0]) if match else 0.0

# Scraper real da OLX (fonte confiável)
def olx_scraper(query):
    url = f"https://www.olx.com.br/brasil?q={query.replace(' ', '-')}"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    itens = soup.select("li.sc-1fcmfeb-2")[:5]  # Pega os 5 primeiros
    resultados = []

    for item in itens:
        nome = item.select_one("h2")
        preco = item.select_one("span.sc-ifAKCX")
        local = item.select_one("span.sc-7l84qu-1")
        link_tag = item.select_one("a")
        preco_num = extrair_preco(preco.text) if preco else 0.0

        resultados.append({
            "Produto": nome.text if nome else "Sem nome",
            "Preço (R$)": preco_num,
            "Loja": "OLX",
            "Link": link_tag["href"] if link_tag else "",
            "Fonte Confiável": True,
            "Local": local.text if local else "Não informado",
            "Fonte": "OLX"
        })

        cursor.execute(
            "INSERT INTO aprendizado (termo, origem, confiavel, preco) VALUES (?, ?, ?, ?)",
            (query, "OLX", True, preco_num)
        )

    conn.commit()
    return resultados

# Fonte simulada (não confiável)
def fonte_simulada(query):
    simulados = []
    for i in range(5):
        preco_simulado = 250 + i * 45
        simulados.append({
            "Produto": f"{query} Simulado {i+1}",
            "Preço (R$)": preco_simulado,
            "Loja": "Shopee/Facebook/WhatsX",
            "Link": "https://example.com/produto",
            "Fonte Confiável": False,
            "Local": "Desconhecido",
            "Fonte": "Fonte Simulada"
        })

        cursor.execute(
            "INSERT INTO aprendizado (termo, origem, confiavel, preco) VALUES (?, ?, ?, ?)",
            (query, "Simulada", False, preco_simulado)
        )

    conn.commit()
    return simulados

# Função unificada
def buscar_em_fontes(query, minimo=10):
    resultados_validos = olx_scraper(query)
    resultados_fakes = fonte_simulada(query)
    resultados = resultados_validos + resultados_fakes

    fontes = [
        f"OLX → {len(resultados_validos)} resultados",
        f"Simulados → {len(resultados_fakes)} resultados"
    ]

    return resultados[:minimo], fontes
