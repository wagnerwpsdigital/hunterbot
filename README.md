# HunterBot – Agente de Busca Inteligente

HunterBot é um sistema inteligente de busca de preços com scraping, filtros, aprendizado e integração com Telegram Bot.

## Como rodar localmente
pip install -r requirements.txt
streamlit run hunterbot_mvp.py

## Docker
docker build -t hunterbot .
docker run -d -p 8501:8501 hunterbot
