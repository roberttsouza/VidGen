import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import streamlit as st
from src.apis.news_api import fetch_bitcoin_news
from src.utils.text_to_speech import text_to_speech
from src.apis.pexels_api import search_images
from src.utils.video_creator import create_video
from src.config import AUDIO_DIR, VIDEOS_DIR
import os
from datetime import datetime

# Configuração inicial do Streamlit
st.set_page_config(
    page_title="CryptoCaster - Gerador de Vídeos Automáticos",
    page_icon="🎥",
    layout="wide"
)

st.title("🎥 CryptoCaster - Gerador de Vídeos Automáticos")
st.markdown("Crie vídeos automáticos com base em notícias sobre Bitcoin.")

# Usar session_state para armazenar as notícias e evitar recarregar tudo
if "news_data" not in st.session_state:
    st.session_state.news_data = []
# Botão para buscar notícias
if st.button("Buscar Notícias"):
    with st.spinner("Buscando notícias..."):
        news = fetch_bitcoin_news()
        if not news:
            st.error("Nenhuma notícia encontrada. Tente novamente mais tarde.")
        else:
            st.session_state.news_data = news  # Armazenar no session_state
            st.success(f"{len(news)} notícias encontradas!")

# Exibir notícias após a busca
if st.session_state.news_data:
    for item in st.session_state.news_data:
        with st.expander(f"📰 {item['title']}"):
            st.write(f"Fonte: {item['source']}")
            st.write(f"Publicado em: {datetime.fromtimestamp(item['published_on']).strftime('%d/%m/%Y')}")
            st.write(f"[Link para a notícia original]({item['url']})")
            
            # Botão para gerar vídeo
            if st.button(f"🎬 Gerar Vídeo para '{item['title']}'", key=f"generate_{item['id']}"):
                with st.spinner(f"Gerando vídeo para '{item['title']}'..."):
                        try:
                            audio_file = f"{AUDIO_DIR}/audio_{item['id']}.mp3"
                            video_file = f"{VIDEOS_DIR}/video_{item['id']}.mp4"

                            # Garantir diretórios existem
                            os.makedirs(os.path.dirname(audio_file), exist_ok=True)
                            os.makedirs(os.path.dirname(video_file), exist_ok=True)

                            # Gerar áudio
                            try:
                                text_to_speech(item["title"] + ". " + item["body"], audio_file)
                                logging.info(f"Áudio gerado em: {audio_file}")
                            except Exception as e:
                                logging.error(f"Erro ao gerar áudio: {str(e)}")
                                st.error(f"Falha ao gerar áudio: {str(e)}")
                                continue

                            logging.info(f"Áudio gerado: {audio_file}")

                            # Verificar existência do áudio
                            if not os.path.exists(audio_file):
                                raise FileNotFoundError(f"Áudio não encontrado: {audio_file}")

                            # Buscar imagens
                            keywords = item["title"].split()[:3]
                            images = search_images(" ".join(keywords), item.get("tags", ""))
                            if not images:
                                images = ["https://via.placeholder.com/1920x1080?text=Bitcoin+News"]

                            # Validar imagens (remove redundância)
                            if not images:
                                images = ["https://via.placeholder.com/1920x1080?text=Bitcoin+News"]

                            # Criar vídeo com rastreamento completo
                            try:
                                logging.info(f"Iniciando criação do vídeo para {item['title']}")
                                create_video(audio_file, images, video_file)
                                logging.info(f"Vídeo finalizado: {video_file}")
                                st.success("Vídeo gerado com sucesso!")
                                st.video(video_file)
                            except Exception as e:
                                logging.error(f"Erro crítico ao criar vídeo: {str(e)}", exc_info=True)
                                st.error("Ocorreu um erro durante a geração do vídeo. Verifique os logs.")
                                continue
                        except Exception as e:
                            logging.error(f"Erro crítico geral: {str(e)}", exc_info=True)
                            st.error("Erro inesperado. Verifique os logs do aplicativo.")
