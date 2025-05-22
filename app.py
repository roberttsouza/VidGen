import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import streamlit as st
from src.apis.news_api import fetch_bitcoin_news
from src.utils.text_to_speech import text_to_speech
from src.utils.video_creator import create_video_synced
from src.config import AUDIO_DIR, VIDEOS_DIR, IMAGES_DIR
import os
import re
from datetime import datetime
import random
import nltk # Para o download de recursos

# --- Configuração do NLTK ---
def setup_nltk_resources():
    resources = [("tokenizers/punkt", "punkt"), ("corpora/stopwords", "stopwords")]
    downloaded_any = False
    for resource_path, resource_id in resources:
        try:
            nltk.data.find(resource_path)
        except LookupError:
            st.info(f"Baixando recurso NLTK necessário: '{resource_id}'...")
            nltk.download(resource_id, quiet=True)
            st.success(f"Recurso '{resource_id}' baixado.")
            downloaded_any = True
    # if downloaded_any:
    #     st.experimental_rerun() # Rerun se algo foi baixado para garantir que o app use
setup_nltk_resources()
# --- Fim Configuração NLTK ---


st.set_page_config(
    page_title="CryptoCaster - Gerador de Vídeos Automáticos",
    page_icon="🎥",
    layout="wide"
)

st.title("🎥 CryptoCaster - Gerador de Vídeos Automáticos")
st.markdown("Crie vídeos automáticos com base em notícias sobre Bitcoin, com imagens sincronizadas.")

def normalize_title_for_file(title):
    normalized = re.sub(r'[^\w\s-]', '', title).strip()
    normalized = re.sub(r'[-\s]+', '_', normalized)
    return normalized[:80] # Reduzido para nomes de arquivo mais curtos

if "news_data" not in st.session_state:
    st.session_state.news_data = []
if "current_video_path" not in st.session_state:
    st.session_state.current_video_path = None

if st.button("Buscar Notícias de Bitcoin"):
    with st.spinner("Buscando notícias..."):
        news = fetch_bitcoin_news()
        if not news:
            st.error("Nenhuma notícia encontrada. Tente novamente mais tarde.")
            st.session_state.news_data = []
        else:
            st.session_state.news_data = news
            st.success(f"{len(news)} notícias encontradas!")
        st.session_state.current_video_path = None # Limpa vídeo anterior

if st.session_state.news_data:
    for index, item in enumerate(st.session_state.news_data):
        news_title = item.get('title', f"Noticia_{index}")
        news_id = str(item.get('id', f"idx{index}_{random.randint(1000,9999)}"))
        
        button_key = f"generate_{news_id}_{normalize_title_for_file(news_title[:20])}"

        with st.expander(f"📰 {news_title}"):
            st.write(f"Fonte: {item.get('source_info', {}).get('name', item.get('source', 'Desconhecida'))}")
            st.write(f"Publicado em: {datetime.fromtimestamp(item['published_on']).strftime('%d/%m/%Y %H:%M')}")
            if item.get('url'):
                st.write(f"[Link para a notícia original]({item['url']})")
            
            body_preview = item.get('body', '')
            st.caption(f"Corpo: {body_preview[:300]}{'...' if len(body_preview) > 300 else ''}")

            if st.button(f"🎬 Gerar Vídeo para '{news_title}'", key=button_key):
                st.session_state.current_video_path = None 
                
                if not body_preview:
                    st.warning("O corpo da notícia está vazio. O vídeo pode não ser muito informativo.")
                
                with st.spinner(f"Gerando vídeo para '{news_title}'... Isso pode levar alguns minutos."):
                    progress_bar = st.progress(0, text="Iniciando...")
                    try:
                        normalized_title_for_file = normalize_title_for_file(news_title)
                        base_filename = f"{normalized_title_for_file}_{news_id}"
                        
                        audio_file = os.path.join(AUDIO_DIR, f"{base_filename}.mp3")
                        video_file = os.path.join(VIDEOS_DIR, f"{base_filename}.mp4")

                        os.makedirs(AUDIO_DIR, exist_ok=True)
                        os.makedirs(VIDEOS_DIR, exist_ok=True)
                        os.makedirs(IMAGES_DIR, exist_ok=True)

                        full_text_for_video = news_title + ". " + body_preview
                        
                        progress_bar.progress(10, text="Passo 1/3: Gerando áudio...")
                        text_to_speech(full_text_for_video, audio_file, lang='en') # Assumindo inglês
                        if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
                            st.error(f"Falha ao gerar áudio ou arquivo de áudio vazio: {audio_file}")
                            raise Exception("Geração de áudio falhou")
                        logging.info(f"Áudio gerado em: {audio_file}")
                        progress_bar.progress(33, text="Áudio gerado. Passo 2/3: Preparando imagens...")
                        
                        create_video_synced(
                            full_text_for_video, 
                            audio_file, 
                            video_file, 
                            news_title=news_title, # Passando o título da notícia
                            words_per_image=8
                        )
                        progress_bar.progress(90, text="Passo 3/3: Renderizando vídeo final...")
                        
                        if not os.path.exists(video_file) or os.path.getsize(video_file) == 0:
                            st.error("Falha na criação do vídeo ou arquivo de vídeo vazio.")
                            raise Exception("Criação de vídeo falhou")

                        logging.info(f"Vídeo finalizado: {video_file}")
                        progress_bar.progress(100, text="Vídeo gerado com sucesso!")
                        st.success("Vídeo gerado com sucesso!")
                        st.session_state.current_video_path = video_file
                    
                    except Exception as e:
                        logging.error(f"Erro crítico durante a geração do vídeo para '{news_title}': {e}", exc_info=True)
                        st.error(f"Ocorreu um erro: {e}. Verifique os logs.")
                        if 'progress_bar' in locals(): progress_bar.empty()
    
    if st.session_state.current_video_path and os.path.exists(st.session_state.current_video_path):
        st.video(st.session_state.current_video_path)
        with open(st.session_state.current_video_path, "rb") as file_content:
            st.download_button(
                label="Baixar Vídeo",
                data=file_content,
                file_name=os.path.basename(st.session_state.current_video_path),
                mime="video/mp4",
                key=f"download_{os.path.basename(st.session_state.current_video_path)}"
            )
    elif st.session_state.current_video_path:
        st.warning(f"Arquivo de vídeo '{st.session_state.current_video_path}' não encontrado. Por favor, gere novamente.")