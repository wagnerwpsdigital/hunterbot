# HunterBot – Inteligência Comercial Automática

HunterBot é um sistema de busca inteligente de preços, com scraping, painel de aprendizado e operação integrada.

## Funcionalidades
- ✅ Busca por palavras-chave com filtros de preço
- 🔍 Retorno por fontes confiáveis e não confiáveis
- 🧠 Aprendizado contínuo das buscas
- 📈 Painel com estatísticas por fonte, preço e comportamento
- 🤖 Bot Telegram (opcional)
- ☁️ Deploy com Docker ou Streamlit Cloud

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run hunterbot_mvp.py
```

## Usar via Docker

```bash
docker build -t hunterbot .
docker run -d -p 8501:8501 hunterbot
```
