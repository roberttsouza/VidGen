import os
from .apis.news_api import fetch_bitcoin_news
from src.utils.text_to_speech import text_to_speech
from src.apis.pexels_api import search_images
from src.utils.video_creator import create_video
from src.config import AUDIO_DIR, VIDEOS_DIR

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
            
            # Buscar imagens relevantes no Pexels
            keywords = item["title"].split()[:3]  # Usar as primeiras 3 palavras do título
            images = search_images(" ".join(keywords), item.get("tags", ""))
            
            # Fallback para imagem padrão se nenhuma imagem for encontrada
            if not images:
                print("Nenhuma imagem válida encontrada. Usando imagem padrão.")
                default_image = "https://via.placeholder.com/1920x1080"
                images = [default_image]

            # Criar vídeo
            video_file = f"{VIDEOS_DIR}/video_{item['id']}.mp4"
            create_video(audio_file, images, video_file)
            
            print(f"Vídeo gerado com sucesso: {video_file}")
        
        except Exception as e:
            print(f"Erro ao processar notícia (ID: {item.get('id')}): {e}")

if __name__ == "__main__":
    main()