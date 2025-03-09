import requests
from src.config import PEXELS_API_KEY

def search_images(title, tags):
    headers = {"Authorization": PEXELS_API_KEY}
    all_images = []
    page = 1

    # Criar lista de palavras-chave combinando título e tags
    keywords = [word for word in title.split() if len(word) > 3]  # Ignorar palavras curtas
    if tags:
        keywords.extend(tags.split(","))
    keywords = list(set(keywords))  # Remover duplicatas

    # Tentar buscar imagens com cada palavra-chave
    for keyword in keywords:
        while len(all_images) < 50:  # Buscar até 50 imagens
            response = requests.get(
                "https://api.pexels.com/v1/search",
                headers=headers,
                params={"query": keyword, "per_page": 15, "page": page}
            )
            if response.status_code == 200:
                photos = response.json().get("photos", [])
                if not photos:
                    break  # Sem mais imagens disponíveis
                image_urls = [photo["src"]["large"] for photo in photos]
                all_images.extend(image_urls)
                page += 1
            else:
                print(f"Erro ao buscar imagens para '{keyword}': {response.status_code}")
                break

    # Filtrar imagens irrelevantes
    filtered_images = [url for url in all_images if is_relevant_image(url)]
    return filtered_images[:50]  # Limitar a 50 imagens

def is_relevant_image(image_url):
    """
    Verifica se uma imagem é relevante com base na URL.
    """
    irrelevant_keywords = [
        "bikini", "beach", "model", "fashion", "wedding", "party", "celebration",
        "vacation", "swimsuit", "woman", "man", "portrait", "people"
    ]
    return not any(keyword in image_url.lower() for keyword in irrelevant_keywords)