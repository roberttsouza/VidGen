import requests
from src.config import PEXELS_API_KEY

def search_images(title, tags):
    headers = {"Authorization": PEXELS_API_KEY}
    all_images = []
    
    # Lista específica de termos relacionados a criptomoedas para enriquecer a busca
    crypto_terms = [
        "cryptocurrency", "bitcoin", "blockchain", "crypto", "fintech", 
        "digital currency", "trading", "finance", "technology", "computer", 
        "network", "mining", "money", "digital", "business", "chart", "graph",
        "investment", "market", "exchange", "wallet", "token", "transaction"
    ]
    
    # Adicionar termos específicos baseados no título
    keywords = [word for word in title.split() if len(word) > 3]  # Ignorar palavras curtas
    if tags:
        keywords.extend(tags.split(","))
    
    # Garantir que haja pelo menos um termo relacionado a criptomoedas
    has_crypto_term = False
    for term in crypto_terms:
        if any(term.lower() in keyword.lower() for keyword in keywords):
            has_crypto_term = True
            break
    
    if not has_crypto_term:
        # Se não tiver nenhum termo de cripto, adicionar explicitamente um
        keywords.append("cryptocurrency")
    
    # Sempre adicionar "bitcoin" nas buscas já que o tema é sobre Bitcoin
    if "bitcoin" not in [k.lower() for k in keywords]:
        keywords.append("Bitcoin")
    
    # Focar em termos mais relevantes e limitar a quantidade
    priority_keywords = ["Bitcoin", "blockchain", "cryptocurrency", "fintech", "digital"]
    search_terms = []
    
    # Primeiro adicionar termos prioritários que estejam na lista de keywords
    for term in priority_keywords:
        if term.lower() in [k.lower() for k in keywords]:
            search_terms.append(term)
    
    # Depois adicionar outros termos de keywords até ter 3 termos
    for term in keywords:
        if term not in search_terms and len(search_terms) < 3:
            search_terms.append(term)
    
    # Se ainda não tiver 3 termos, adicionar da lista de termos de cripto
    while len(search_terms) < 3:
        for term in crypto_terms:
            if term not in search_terms and len(search_terms) < 3:
                search_terms.append(term)
    
    print(f"Termos de busca: {search_terms}")  # Log para depuração
    
    # Buscar imagens com termos combinados primeiro
    combined_query = " ".join(search_terms[:2])  # Combinar os primeiros dois termos
    try:
        response = requests.get(
            "https://api.pexels.com/v1/search",
            headers=headers,
            params={"query": combined_query, "per_page": 25, "page": 1}
        )
        if response.status_code == 200:
            photos = response.json().get("photos", [])
            image_urls = [photo["src"]["large"] for photo in photos]
            all_images.extend(image_urls)
    except Exception as e:
        print(f"Erro na busca combinada: {e}")
    
    # Buscar por cada termo individual
    for term in search_terms:
        if len(all_images) >= 50:
            break  # Já temos imagens suficientes
            
        try:
            response = requests.get(
                "https://api.pexels.com/v1/search",
                headers=headers,
                params={"query": term, "per_page": 15, "page": 1}
            )
            if response.status_code == 200:
                photos = response.json().get("photos", [])
                image_urls = [photo["src"]["large"] for photo in photos]
                all_images.extend(image_urls)
        except Exception as e:
            print(f"Erro ao buscar imagens para '{term}': {e}")
            continue
    
    # Lista expandida de termos irrelevantes para filtragem
    irrelevant_keywords = [
        "bikini", "beach", "model", "fashion", "wedding", "party", "celebration",
        "vacation", "swimsuit", "woman", "man", "portrait", "people", "person",
        "dance", "dancer", "dancing", "girl", "boy", "kid", "child", "baby", 
        "animal", "pet", "dog", "cat", "food", "meal", "restaurant", "cooking",
        "kitchen", "bedroom", "bathroom", "travel", "holiday", "tourist", "selfie",
        "makeup", "beauty", "cosmetic", "sport", "game", "play", "athlete",
        "concert", "music", "band", "singer", "actor", "actress", "movie", "cinema",
        "drink", "alcohol", "bar", "club", "pub", "flower", "plant", "landscape",
        "mountain", "lake", "ocean", "sea", "river", "forest", "tree", "garden",
        "park", "farm", "farmer", "countryside", "castle", "landmark", "building"
    ]
    
    # Filtrar imagens irrelevantes
    filtered_images = []
    for url in all_images:
        url_lower = url.lower()
        if not any(keyword in url_lower for keyword in irrelevant_keywords):
            filtered_images.append(url)
    
    # Se ficamos sem imagens após a filtragem, adicionar alguns fallbacks específicos
    if not filtered_images:
        print("Após filtragem, não restaram imagens. Usando imagens padrão de cripto.")
        return [
            "https://images.pexels.com/photos/844124/pexels-photo-844124.jpeg",  # Bitcoin
            "https://images.pexels.com/photos/6770610/pexels-photo-6770610.jpeg", # Crypto
            "https://images.pexels.com/photos/7788009/pexels-photo-7788009.jpeg"  # Blockchain
        ]
    
    # Limitar a 10 imagens para garantir melhor qualidade de seleção
    return filtered_images[:10]

def is_relevant_image(image_url):
    """
    Este método está sendo mantido para compatibilidade, mas não é mais usado.
    A filtragem é feita diretamente na função search_images.
    """
    return True