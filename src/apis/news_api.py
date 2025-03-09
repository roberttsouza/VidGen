import requests
from datetime import datetime

def fetch_bitcoin_news():
    try:
        response = requests.get(
            "https://min-api.cryptocompare.com/data/v2/news/",
            params={"lang": "EN", "categories": "BTC,Bitcoin,Crypto,Blockchain"}
        )
        response.raise_for_status()  # Levanta um erro se a resposta não for bem-sucedida
        data = response.json().get("Data", [])
        
        # Filtrar notícias recentes (últimos 7 dias)
        one_week_ago = datetime.now().timestamp() - (7 * 24 * 60 * 60)
        recent_news = [
            item for item in data
            if item.get("published_on", 0) > one_week_ago
        ]
        
        print(f"Notícias encontradas: {len(recent_news)}")  # Log para depuração
        return recent_news
    except Exception as e:
        print(f"Erro ao buscar notícias: {e}")
        return []