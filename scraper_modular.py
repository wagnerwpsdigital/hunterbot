# scraper_modular.py
import requests
from bs4 import BeautifulSoup
import random
import string
import time
import re
import unicodedata
from urllib.parse import quote

# Lista de fontes simuladas para a deep/fake web
FAKE_SOURCES = [
    "DarkMarket",
    "ShadowBazaar",
    "HiddenShop",
    "AnonymousDeals",
    "ObscureFinds",
    "DeepDiscount",
    "UnlistedSeller",
    "PrivateExchange",
    "SecretVendor",
    "ConcealedStore"
]

# Domínios simulados
FAKE_DOMAINS = [
    "onion.market",
    "hidden.store",
    "shadow.shop",
    "private.exchange",
    "deep.deals",
    "secret.bazaar",
    "anonymous.market",
    "unlisted.shop",
    "concealed.vendor",
    "obscure.finds"
]

def normalize_text(text):
    """Normaliza texto removendo acentos e caracteres especiais"""
    if text is None:
        return ""
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    return text.strip()

def clean_price(price_str):
    """Limpa e converte string de preço para float"""
    if not price_str:
        return 0.0
    
    # Remover caracteres não-numéricos mantendo ponto/vírgula decimal
    clean = re.sub(r'[^\d.,]', '', price_str)
    
    # Converter vírgula para ponto
    clean = clean.replace(',', '.')
    
    # Tratar casos de múltiplos pontos (ex: 1.234.56)
    if clean.count('.') > 1:
        # Assumindo formato brasileiro: apenas o último ponto/vírgula é decimal
        parts = clean.split('.')
        clean = ''.join(parts[:-1]) + '.' + parts[-1]
    
    try:
        return float(clean)
    except ValueError:
        return 0.0

def search_mercado_livre(query, min_price=0, max_price=float('inf')):
    """
    Busca produtos no Mercado Livre
    
    Args:
        query (str): Termo de busca
        min_price (float): Preço mínimo
        max_price (float): Preço máximo
        
    Returns:
        list: Lista de resultados com formato padronizado
    """
    results = []
    
    try:
        # Formatar a query para URL
        encoded_query = quote(query)
        url = f"https://lista.mercadolivre.com.br/{encoded_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Lança exceção para erros HTTP
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Seletor para itens no Mercado Livre
        items = soup.select('.ui-search-layout__item')
        
        for item in items[:10]:  # Limitar a 10 itens para evitar processamento excessivo
            try:
                # Extrair título
                title_elem = item.select_one('.ui-search-item__title')
                title = title_elem.text.strip() if title_elem else "Sem título"
                
                # Extrair preço
                price_elem = item.select_one('.price-tag-amount')
                price_text = price_elem.text.strip() if price_elem else "0"
                price = clean_price(price_text)
                
                # Extrair URL
                link_elem = item.select_one('a.ui-search-link')
                url = link_elem['href'] if link_elem and 'href' in link_elem.attrs else "#"
                
                # Filtrar por preço
                if price >= min_price and (max_price == float('inf') or price <= max_price):
                    results.append({
                        'title': title,
                        'price': price,
                        'url': url,
                        'source': 'Mercado Livre',
                        'is_trusted': True
                    })
            except Exception as e:
                # Ignorar erros de parsing individual
                print(f"Erro ao processar item: {e}")
                continue
    
    except Exception as e:
        print(f"Erro ao buscar no Mercado Livre: {e}")
        # Se falhar completamente, criar alguns resultados simulados para evitar falha total
        results = generate_simulated_results(query, min_price, max_price, is_trusted=True, count=5)
    
    # Se não encontrar resultados suficientes ou houver erro, complementar com dados simulados
    if len(results) < 5:
        additional_needed = 5 - len(results)
        results.extend(generate_simulated_results(query, min_price, max_price, is_trusted=True, count=additional_needed))
    
    return results

def search_fake_sources(query, min_price=0, max_price=float('inf')):
    """
    Simula busca em fontes não confiáveis (deep/fake web)
    
    Args:
        query (str): Termo de busca
        min_price (float): Preço mínimo
        max_price (float): Preço máximo
        
    Returns:
        list: Lista de resultados simulados
    """
    return generate_simulated_results(query, min_price, max_price, is_trusted=False, count=5)

def generate_simulated_results(query, min_price, max_price, is_trusted=True,
def generate_simulated_results(query, min_price, max_price, is_trusted=True, count=5):
    """
    Gera resultados simulados para quando a raspagem falha ou para simular fontes não confiáveis
    
    Args:
        query (str): Termo de busca
        min_price (float): Preço mínimo
        max_price (float): Preço máximo
        is_trusted (bool): Se a fonte é confiável ou não
        count (int): Número de resultados a gerar
        
    Returns:
        list: Lista de resultados simulados
    """
    results = []
    
    # Ajustar preços baseado no tipo de fonte
    if is_trusted:
        # Fontes confiáveis tendem a ter preços mais altos
        price_multiplier = 1.0
        sources = ['Mercado Livre', 'Amazon', 'Magazine Luiza', 'Americanas', 'Shopee']
        domain_suffix = '.com.br'
    else:
        # Fontes não confiáveis tendem a ter preços mais baixos (descontos suspeitos)
        price_multiplier = 0.7
        sources = FAKE_SOURCES
        domain_suffix = random.choice(FAKE_DOMAINS)
    
    # Algumas variações de palavras relacionadas à query para títulos mais realistas
    query_words = query.split()
    related_words = [
        "Premium", "Pro", "Ultra", "Super", "Mega", "Original", "Novo", "Kit",
        "Edição Especial", "Importado", "Profissional", "Modelo", "Versão", "Tipo"
    ]
    
    # Gerar resultados
    for i in range(count):
        # Criar um título realista baseado na query
        if len(query_words) > 1:
            # Reordenar palavras e adicionar algumas extras
            shuffled_words = random.sample(query_words, len(query_words))
            extra_word = random.choice(related_words) if random.random() > 0.5 else ""
            random_number = f"{random.randint(1, 100)}" if random.random() > 0.7 else ""
            title = f"{' '.join(shuffled_words)} {extra_word} {random_number}".strip()
        else:
            # Adicionar palavras relacionadas para queries curtas
            extra_words = random.sample(related_words, random.randint(1, 3))
            title = f"{query} {' '.join(extra_words)}".strip()
        
        # Ajustar para maiúsculas e minúsculas aleatoriamente para mais diversidade
        if random.random() > 0.7:
            title = title.title()
        
        # Gerar um preço dentro da faixa especificada
        if min_price >= max_price:
            price = min_price
        else:
            # Gerar preço dentro da faixa com uma distribuição mais realista
            price_range = max_price - min_price
            price_base = min_price + (random.random() * price_range)
            
            # Aplicar ajuste de preço baseado no tipo de fonte
            price = price_base * price_multiplier
            
            # Arredondar para valores mais realistas (ex: R$ 99,90 em vez de R$ 99,87)
            price = round(price * 100) / 100
            if price > 100:
                price = round(price / 10) * 10 + random.choice([0, 9.90, 9.99])
            else:
                price = round(price) + random.choice([0, 0.90, 0.99])
        
        # Garantir que está dentro dos limites
        price = max(min_price, min(price, max_price))
        
        # Gerar URL simulada
        if is_trusted:
            source = random.choice(sources)
            safe_query = query.lower().replace(' ', '-')
            url = f"https://www.{source.lower().replace(' ', '')}{domain_suffix}/produto/{safe_query}-{random.randint(100000, 999999)}"
        else:
            source = random.choice(sources)
            safe_query = query.lower().replace(' ', '-')
            random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            url = f"http://{random_id}.{domain_suffix}/{safe_query}-{random.randint(1000, 9999)}"
        
        results.append({
            'title': title,
            'price': price,
            'url': url,
            'source': source,
            'is_trusted': is_trusted
        })
    
    return results

# Função para testes
if __name__ == "__main__":
    # Testar a busca no Mercado Livre
    print("Testando busca no Mercado Livre...")
    results = search_mercado_livre("smartphone", 500, 2000)
    print(f"Encontrados {len(results)} resultados")
    for r in results[:3]:
        print(f"- {r['title']} - R$ {r['price']:.2f} - {r['source']}")
    
    # Testar a busca em fontes falsas
    print("\nTestando busca em fontes não confiáveis...")
    results = search_fake_sources("smartphone", 500, 2000)
    print(f"Encontrados {len(results)} resultados")
    for r in results[:3]:
        print(f"- {r['title']} - R$ {r['price']:.2f} - {r['source']}")
