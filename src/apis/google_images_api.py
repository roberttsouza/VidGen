import requests
from src.config import GOOGLE_API_KEY, GOOGLE_CSE_ID
import logging

# Configuração do logging para este módulo, se necessário, ou confie no logging global
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_google_images(query: str, num_images: int = 1):
    """
    Busca imagens no Google usando a Custom Search JSON API.
    Retorna uma lista de URLs de imagens.
    """
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        logging.error("Google API Key ou CSE ID não configurados.")
        return []

    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_CSE_ID,
        'q': query,
        'searchType': 'image',
        'num': num_images,
        'imgSize': 'large', # ou 'xlarge' para melhor qualidade, mas pode demorar mais
        'safe': 'medium' # ou 'high'
    }

    try:
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json()
        
        image_urls = []
        if "items" in results:
            for item in results.get("items", []):
                image_urls.append(item.get("link"))
        
        if not image_urls:
            logging.warning(f"Nenhuma imagem encontrada no Google para: '{query}'")
        else:
            logging.info(f"Google Images encontrou para '{query}': {image_urls[:num_images]}")
        return image_urls[:num_images]

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao buscar imagens no Google para '{query}': {e}")
        return []
    except Exception as e:
        logging.error(f"Erro inesperado ao processar busca no Google para '{query}': {e}")
        return []

if __name__ == '__main__':
    # Teste rápido
    logging.basicConfig(level=logging.INFO)
    test_query = "Bitcoin price chart"
    urls = search_google_images(test_query, 2)
    if urls:
        print(f"Imagens para '{test_query}':")
        for url in urls:
            print(url)
    else:
        print(f"Nenhuma imagem encontrada para '{test_query}'. Verifique as chaves da API e CSE ID.")