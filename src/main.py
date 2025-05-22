import os
import re
import logging
from datetime import datetime
from src.apis.news_api import fetch_bitcoin_news
from src.utils.text_to_speech import text_to_speech
from src.utils.video_creator import create_video_synced
from src.config import AUDIO_DIR, VIDEOS_DIR, IMAGES_DIR
import random
import nltk # Para o download de recursos

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuração do NLTK ---
def setup_nltk_resources_cli():
    resources = [("tokenizers/punkt", "punkt"), ("corpora/stopwords", "stopwords")]
    for resource_path, resource_id in resources:
        try:
            nltk.data.find(resource_path)
        except LookupError:
            logging.info(f"Baixando recurso NLTK necessário: '{resource_id}'...")
            nltk.download(resource_id, quiet=True)
            logging.info(f"Recurso '{resource_id}' baixado.")
setup_nltk_resources_cli()
# --- Fim Configuração NLTK ---


def normalize_title_for_file_cli(title):
    normalized = re.sub(r'[^\w\s-]', '', title).strip()
    normalized = re.sub(r'[-\s]+', '_', normalized)
    return normalized[:80]

def main_cli():
    logging.info("Iniciando CryptoCaster CLI...")
    news_items = fetch_bitcoin_news()
    if not news_items:
        logging.info("Nenhuma notícia encontrada. Encerrando.")
        return

    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)

    # Processar apenas as X primeiras para teste CLI, ou todas
    num_news_to_process = min(len(news_items), 2) # Processa até 2 notícias
    logging.info(f"Processando {num_news_to_process} notícias...")

    for item in news_items[:num_news_to_process]:
        news_title = item.get('title', "NoticiaDesconhecida")
        news_id = str(item.get('id', f"cli_id_{random.randint(1000,9999)}"))
        news_body = item.get("body", "")

        try:
            logging.info(f"Processando notícia: {news_title}")
            
            if not news_body:
                 logging.warning(f"Notícia '{news_title}' não possui corpo. O vídeo pode ser menos informativo.")

            full_text_for_video = news_title + ". " + news_body

            normalized_title = normalize_title_for_file_cli(news_title)
            base_filename = f"{normalized_title}_{news_id}"

            audio_file = os.path.join(AUDIO_DIR, f"{base_filename}.mp3")
            video_output_file = os.path.join(VIDEOS_DIR, f"{base_filename}.mp4")

            logging.info(f"Gerando áudio para '{news_title}' em {audio_file}...")
            text_to_speech(full_text_for_video, audio_file, lang='en') # Assumindo inglês
            if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
                logging.error(f"Falha ao gerar áudio ou áudio vazio: {audio_file}")
                continue
            logging.info(f"Áudio gerado: {audio_file}")

            logging.info(f"Gerando vídeo para '{news_title}' em {video_output_file}...")
            create_video_synced(
                full_text=full_text_for_video,
                audio_file=audio_file,
                output_video_file=video_output_file,
                news_title=news_title, # Passando o título da notícia
                words_per_image=8
            )
            if not os.path.exists(video_output_file) or os.path.getsize(video_output_file) == 0:
                 logging.error(f"Falha na criação do vídeo ou arquivo de vídeo vazio: {video_output_file}")
                 continue
            logging.info(f"Vídeo gerado com sucesso: {video_output_file}")

        except Exception as e:
            logging.error(f"Erro ao processar notícia ID {news_id} - Título: {news_title}: {e}", exc_info=True)
            continue 

    logging.info("Processo CLI CryptoCaster concluído.")

if __name__ == "__main__":
    main_cli()