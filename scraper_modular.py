import requests
from bs4 import BeautifulSoup
import re
import time
import sqlite3

HEADERS = {"User-Agent": "Mozilla/5.0"}

conn = sqlite3.connect("hunterbot_memoria.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS aprendizado (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    termo TEXT,
    origem TEXT,
    confiavel BOOLEAN,
    preco REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

def extrair_preco(preco_str):
    preco_str = preco_str.replace(".", "").replace(",", ".")
    match = re.findall(r"\d+\.\d+", preco_str)
    return float(match[0]) if match else 0.0

def mercadolivre_scraper(query):
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={query}"
    res = requests.get(url)
    if res.status_code != 200:
        return []
    data = res.json()
    resultados = []
    for item in data.get("results", [])[:5]:
        resultados.append({
            "Produto": item.get("title", "Sem nome"),
            "Preço (R$)": float(item.get("price", 0.0)),
            "Loja": "Mercado Livre API",
            "Link": item.get("permalink", ""),
            "Fonte Confiável": True,
            "Local": item.get("address", {}).get("state_name", "Desconhecido"),
            "Fonte": "Mercado Livre API"
        })
        # Registro no banco para aprendizado
        cursor.execute(
            "INSERT INTO aprendizado (termo, origem, confiavel, preco) VALUES (?, ?, ?, ?)",
            (query, "Mercado Livre API", True, item.get("price", 0.0))
        )
    conn.commit()
    return resultados
    for item in itens:
        nome = item.select_one(".ui-search-item__title")
        preco = item.select_one(".price-tag-fraction")
        link = item.select_one("a")
        preco_valor = float(preco.text.replace(".", "")) if preco else 0.0

        resultados.append({
            "Produto": nome.text if nome else "Sem nome",
            "Preço (R$)": preco_valor,
            "Loja": "Mercado Livre",
            "Link": link['href'] if link else "",
            "Fonte Confiável": True,
            "Local": "Brasil",
            "Fonte": "Mercado Livre"
        })

        cursor.execute("INSERT INTO aprendizado (termo, origem, confiavel, preco) VALUES (?, ?, ?, ?)",
                       (query, "Mercado Livre", True, preco_valor))

    conn.commit()
    return resultados

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
            "Fonte": "Fonte Simulada (Deep/Fake)"
        })

        cursor.execute("INSERT INTO aprendizado (termo, origem, confiavel, preco) VALUES (?, ?, ?, ?)",
                       (query, "Simulada", False, preco_simulado))

    conn.commit()
    return simulados

def buscar_em_fontes(query, minimo=10):
    resultados_surface = mercadolivre_scraper(query)
    resultados_fake = fonte_simulada(query)

    resultados = resultados_surface + resultados_fake
    fontes = [
        f"Mercado Livre → {len(resultados_surface)} resultados",
        f"Simulados (Deep/Fake) → {len(resultados_fake)} resultados"
    ]

    return resultados[:minimo], fontes
