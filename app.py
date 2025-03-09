import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import streamlit as st
from src.apis.news_api import fetch_bitcoin_news
from src.utils.text_to_speech import text_to_speech
from src.apis.pexels_api import search_images
from src.utils.video_creator import create_video
from src.config import AUDIO_DIR, VIDEOS_DIR
import os
import re
from datetime import datetime

# Configuração inicial do Streamlit
st.set_page_config(
    page_title="CryptoCaster - Gerador de Vídeos Automáticos",
    page_icon="🎥",
    layout="wide"
)

st.title("🎥 CryptoCaster - Gerador de Vídeos Automáticos")
st.markdown("Crie vídeos automáticos com base em notícias sobre Bitcoin.")

# Função para normalizar título (remover caracteres especiais)
def normalize_title(title):
    # Substituir caracteres especiais e espaços por underscores
    normalized = re.sub(r'[^\w\s]', '', title)
    normalized = normalized.replace(' ', '_')
    # Limitar tamanho para evitar nomes de arquivo muito longos
    if len(normalized) > 100:
        normalized = normalized[:100]
    return normalized

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
                            # Criar nome de arquivo baseado no título da notícia
                            normalized_title = normalize_title(item['title'])
                            
                            audio_file = f"{AUDIO_DIR}/audio_{item['id']}.mp3"
                            video_file = f"{VIDEOS_DIR}/{normalized_title}.mp4"

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

                            # Buscar imagens com as palavras-chave retiradas do título, categorias e tags
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
                            
                            st.text(f"Buscando imagens para: {' '.join(keywords[:3])} com tags: {tags}")
                            images = search_images(" ".join(keywords[:3]), tags)
                            
                            if not images:
                                logging.warning("Nenhuma imagem relevante encontrada. Usando imagem padrão.")
                                images = ["https://images.pexels.com/photos/844124/pexels-photo-844124.jpeg"]
                                st.warning("Nenhuma imagem relevante encontrada. Usando imagem padrão de Bitcoin.")

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