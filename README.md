# 🤖 HunterBot – Inteligência Comercial Automatizada

HunterBot é um sistema automatizado de busca inteligente de produtos, que usa scraping, aprendizado contínuo e painel de insights em tempo real. Desenvolvido para auxiliar tomadas de decisão em compras, prospecções e análise de mercado.

---

## 🚀 Funcionalidades

- 🔎 Busca de produtos por palavra-chave
- 🎯 Filtros por faixa de preço e região
- 📦 Classificação por fontes confiáveis e não confiáveis
- 📈 Aprendizado contínuo com banco de dados local (SQLite)
- 📊 Painel de uso com históricos e tendências
- 🤖 Integração com Telegram Bot (opcional)
- ☁️ Deploy via Docker ou Streamlit Cloud

---

## 🛠️ Tecnologias Utilizadas

- `Python 3.10`
- `Streamlit`
- `BeautifulSoup4 + Requests`
- `SQLite3`
- `pandas / matplotlib / geopy`
- `python-telegram-bot==20.7`

---

## 🧩 Como rodar localmente

```bash
git clone https://github.com/SEU_USUARIO/hunterbot.git
cd hunterbot

# Instalar dependências
pip install -r requirements.txt

# Rodar aplicação
streamlit run hunterbot_mvp.py
