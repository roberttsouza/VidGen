import os
import re
from .apis.news_api import fetch_bitcoin_news
from src.utils.text_to_speech import text_to_speech
from src.apis.pexels_api import search_images
from src.utils.video_creator import create_video
from src.config import AUDIO_DIR, VIDEOS_DIR

def normalize_title(title):
    # Substituir caracteres especiais e espaços por underscores
    normalized = re.sub(r'[^\w\s]', '', title)
    normalized = normalized.replace(' ', '_')
    # Limitar tamanho para evitar nomes de arquivo muito longos
    if len(normalized) > 100:
        normalized = normalized[:100]
    return normalized

def main():
    # Buscar notícias recentes sobre Bitcoin
    news = fetch_bitcoin_news()
    if not news:
        print("Nenhuma notícia encontrada. Encerrando o processo.")
        return

    for item in news:
        try:
            # Gerar áudio
            audio_file = f"{AUDIO_DIR}/audio_{item['id']}.mp3"
            text_to_speech(item["title"] + ". " + item["body"], audio_file)
            
            # Buscar imagens relevantes com estratégia melhorada
            # Extrair termos relevantes do título
            keywords = [w for w in item["title"].split() if len(w) > 3]
            
            # Verificar se há termos sobre blockchain ou crypto no título
            crypto_terms = ["bitcoin", "blockchain", "crypto", "token", "whale", 
                           "transaction", "trading", "market", "nft", "currency"]
            
            # Adicionar "bitcoin" e "cryptocurrency" às palavras-chave se não houver
            # termos relacionados no título
            has_crypto_term = any(term in item["title"].lower() for term in crypto_terms)
            if not has_crypto_term:
                keywords.append("bitcoin")
                keywords.append("cryptocurrency")
            
            # Obter tags da notícia
            tags = item.get("tags", "")
            if not tags:
                tags = "bitcoin,cryptocurrency,blockchain,finance,technology"
            
            print(f"Buscando imagens para: {' '.join(keywords[:3])} com tags: {tags}")
            images = search_images(" ".join(keywords[:3]), tags)
            
            # Fallback para imagem padrão se nenhuma imagem for encontrada
            if not images:
                print("Nenhuma imagem válida encontrada. Usando imagem padrão de Bitcoin.")
                default_images = [
                    "https://images.pexels.com/photos/844124/pexels-photo-844124.jpeg",  # Bitcoin
                    "https://images.pexels.com/photos/6770610/pexels-photo-6770610.jpeg", # Crypto
                    "https://images.pexels.com/photos/7788009/pexels-photo-7788009.jpeg"  # Blockchain
                ]
                images = default_images
            
            # Normalizar título para o nome do arquivo
            normalized_title = normalize_title(item['title'])
            
            # Criar vídeo
            video_file = f"{VIDEOS_DIR}/{normalized_title}.mp4"
            create_video(audio_file, images, video_file)
            
            print(f"Vídeo gerado com sucesso: {video_file}")

        except Exception as e:
            print(f"Erro ao processar notícia (ID: {item.get('id')}): {e}")

if __name__ == "__main__":
    main()