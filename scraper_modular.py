import requests
from bs4 import BeautifulSoup
import re

HEADERS = {"User-Agent": "Mozilla/5.0"}

def extrair_preco(preco_str):
    preco_str = preco_str.replace(".", "").replace(",", ".")
    match = re.findall(r"\d+\.\d+", preco_str)
    return float(match[0]) if match else 0.0

def google_shopping_scraper(query):
    url = f"https://www.google.com/search?tbm=shop&q={query.replace(' ', '+')}"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    resultados = []
    for item in soup.select(".sh-dgr__grid-result"):
        nome = item.select_one(".tAxDx")
        preco = item.select_one(".a8Pemb")
        loja = item.select_one(".aULzUe")
        link = item.select_one("a")
        resultados.append({
            "Produto": nome.text if nome else "Sem nome",
            "Preço (R$)": extrair_preco(preco.text) if preco else 0.0,
            "Loja": loja.text if loja else "Sem loja",
            "Link": f"https://www.google.com{link['href']}" if link else "",
            "Fonte Confiável": True,
            "Local": "Não informado",
            "Fonte": "Google Shopping"
        })
    return resultados

def buscar_em_fontes(query, minimo=10):
    resultados = google_shopping_scraper(query)
    return resultados[:minimo], [f"Google Shopping → {len(resultados)} resultados"]# Scrapers modulares por fonte (resumo)
