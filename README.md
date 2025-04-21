# HunterBot - Agente de Inteligência Digital

O HunterBot é um agente digital automatizado que busca produtos, serviços e informações sob demanda, comparando fontes confiáveis (surface web) e não confiáveis ou simuladas (deep/fake web). O sistema aprende com o uso e fornece insights analíticos baseados nas buscas realizadas.

## 🔍 Funcionalidades

- **Busca inteligente**: Encontra pelo menos 10 resultados por busca (5 de fontes confiáveis, 5 de fontes não confiáveis)
- **Filtros de preço**: Permite buscar produtos dentro de uma faixa de preço específica
- **Análise de dados**: Oferece insights sobre preços, fontes mais confiáveis e tendências
- **Histórico de buscas**: Armazena todas as pesquisas anteriores para consulta
- **Aprendizado contínuo**: Melhora os resultados com base nos padrões de uso
- **Interface web e bot Telegram**: Acesse por diferentes canais

## 🛠️ Tecnologias

- **Backend**: Python, SQLite
- **Frontend**: Streamlit
- **Web Scraping**: BeautifulSoup, Requests
- **Análise de Dados**: Pandas, Matplotlib, Seaborn
- **Integração**: API Telegram Bot

## 📊 Interface e Painéis

- **Painel de busca**: Filtros por termo e preço
- **Visualização de resultados**: Separação clara entre fontes confiáveis e não confiáveis
- **Painel analítico**: Gráficos de tendências, termos mais buscados e preços médios
- **Dashboard de aprendizado**: Insights e recomendações baseados no histórico

## 📋 Requisitos

- Python 3.8+
- As bibliotecas listadas em `requirements.txt`
- Para o bot do Telegram: Token de API do Telegram Bot

## 🚀 Instalação e Uso

### Instalação Local

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/hunterbot.git
cd hunterbot
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o aplicativo Streamlit:
```bash
streamlit run hunterbot_mvp.py
```

### Usando Docker

1. Construa a imagem Docker:
```bash
docker build -t hunterbot .
```

2. Execute o contêiner:
```bash
docker run -p 8501:8501 hunterbot
```

3. Acesse o aplicativo no navegador:
```
http://localhost:8501
```

### Configuração do Bot do Telegram (opcional)

1. Crie um arquivo `.env` na raiz do projeto com o token do seu bot:
```
TELEGRAM_BOT_TOKEN=seu_token_aqui
```

2. Execute o bot do Telegram:
```bash
python hunterbot_telegram_bot.py
```

## 🔌 Integração e Extensibilidade

O HunterBot foi projetado para ser extremamente flexível:

- **APIs adicionais**: Integre facilmente com outras fontes de dados
- **Backends alternativos**: Suporte para migração para Supabase/Firebase
- **Canais de comunicação**: Possibilidade de integração com WhatsApp, Discord, etc.
- **Sistemas corporativos**: Preparado para integração com CRMs, ERPs e outros sistemas

## 📜 Estrutura de Arquivos

- `hunterbot_mvp.py` - Interface principal e painel
- `scraper_modular.py` - Módulo com scraping (Mercado Livre + simulado)
- `requirements.txt` - Dependências do projeto
- `Dockerfile` - Configuração para ambiente containerizado
- `hunterbot_telegram_bot.py` - Integração com Telegram
- `README.md` - Este arquivo de documentação

## 📝 Notas Importantes

- O sistema usa web scraping para fontes confiáveis. Certifique-se de estar em conformidade com os Termos de Serviço das plataformas que está acessando.
- As fontes "não confiáveis" são simuladas para fins de demonstração.
- O bot armazena dados em SQLite localmente. Para uma implementação em produção, considere usar um banco de dados mais robusto.

## 📋 Próximos Passos

- Migração para framework web mais robusto (Flask/FastAPI)
- Implementação de autenticação de usuários
- Adição de mais fontes de dados reais
- Refinamento do algoritmo de aprendizado
- Expansão das capacidades de análise de dados

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
