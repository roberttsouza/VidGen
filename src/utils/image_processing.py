from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from PIL import Image, ImageOps
import numpy as np
import os
import re # Para expressões regulares na extração de keywords
import logging
from src.config import IMAGES_DIR

# Certifique-se de que o diretório de imagens existe
os.makedirs(IMAGES_DIR, exist_ok=True)

# Carregar stopwords uma vez
try:
    stop_words_lang = stopwords.words('english') # Mude para 'portuguese' se o texto for em PT
except LookupError:
    import nltk
    logging.info("Baixando recurso 'stopwords' do NLTK...")
    nltk.download('stopwords', quiet=True)
    stop_words_lang = stopwords.words('english')


def extract_entities_and_keywords_for_search(text_chunk: str, original_news_title: str = "") -> str:
    """
    Extrai entidades e palavras-chave de um trecho de texto para busca de imagens.
    Prioriza termos mais longos e tenta manter frases curtas.
    Adiciona contexto do título da notícia se o chunk for muito genérico.
    """
    # Tenta identificar nomes próprios capitalizados primeiro (ex: "Donald Trump", "Bitcoin Cash")
    # Esta é uma heurística e pode ser melhorada com NER completo
    proper_nouns_matches = re.findall(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)", text_chunk)
    if proper_nouns_matches:
        # Pega o nome próprio mais longo encontrado no chunk
        longest_proper_noun = max(proper_nouns_matches, key=len)
        # Se o nome próprio compõe a maior parte do chunk, use-o diretamente
        if len(longest_proper_noun) > len(text_chunk) * 0.6:
            logging.info(f"Priorizando nome próprio: '{longest_proper_noun}' do chunk: '{text_chunk}'")
            return longest_proper_noun.strip()

    word_tokens = word_tokenize(text_chunk.lower())
    
    keywords = [
        word for word in word_tokens 
        if word.isalnum() and word not in stop_words_lang and len(word) >= 3
    ]

    if not keywords and len(word_tokens) <= 4 : # Se poucas palavras e todas stopwords
        keywords = [word for word in word_tokens if word.isalnum()] # Usa todas as alfanuméricas

    if not keywords:
        # Se o chunk original é curto e não gerou keywords, use o chunk original
        if len(text_chunk.split()) <= 3:
             search_query = text_chunk.strip()
        else: # Se mais longo, pegar as primeiras palavras do chunk original
            search_query = " ".join(text_chunk.split()[:3]).strip()
    else:
        # Usa as primeiras 3 keywords significativas, ou todas se menos de 3
        search_query = " ".join(keywords[:3])

    # Contextualização com o título da notícia
    if len(search_query.split()) < 2 and original_news_title:
        title_main_subject = ""
        # Tenta pegar um nome próprio do título
        title_proper_nouns = re.findall(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)", original_news_title)
        if title_proper_nouns:
            title_main_subject = max(title_proper_nouns, key=len).lower()
        
        if not title_main_subject: # Se não achou nome próprio, pega keywords do título
            title_keywords = [
                word for word in word_tokenize(original_news_title.lower())
                if word.isalnum() and word not in stop_words_lang and len(word) >= 4
            ]
            if title_keywords:
                title_main_subject = title_keywords[0]
        
        if title_main_subject and title_main_subject not in search_query.lower():
            search_query = title_main_subject + " " + search_query
            search_query = " ".join(search_query.split()[:4]) # Limita o tamanho da query combinada

    # Fallback final e limpeza
    search_query = search_query.strip()
    if not search_query or len(search_query) < 3 : # Se query muito curta ou vazia
        # Se o chunk original era algo, usa ele. Senão, fallback genérico.
        if text_chunk.strip() and len(text_chunk.strip()) >=3 :
            search_query = text_chunk.strip()
        else:
            search_query = "Bitcoin cryptocurrency" # Fallback genérico sobre o tema

    # Evitar termos muito genéricos sozinhos
    generic_terms = ["image", "photo", "picture", "graph", "chart", "data", "report", "news"]
    query_words = search_query.lower().split()
    if len(query_words) == 1 and query_words[0] in generic_terms:
        search_query = "Bitcoin " + search_query # Adiciona contexto

    logging.info(f"Texto chunk: '{text_chunk}' | Título: '{original_news_title}' -> Query para imagem: '{search_query}'")
    return search_query


def resize_and_crop_image(image_path, output_size=(1920, 1080)):
    """
    Redimensiona e corta a imagem para o aspect ratio 16:9 (output_size),
    cortando o excesso do centro.
    """
    try:
        img = Image.open(image_path)
        img = ImageOps.exif_transpose(img) 

        target_aspect = output_size[0] / output_size[1]
        img_width, img_height = img.size
        img_aspect = img_width / img_height

        if img_aspect > target_aspect:
            new_width = int(target_aspect * img_height)
            offset = (img_width - new_width) // 2
            img = img.crop((offset, 0, img_width - offset, img_height))
        elif img_aspect < target_aspect:
            new_height = int(img_width / target_aspect)
            offset = (img_height - new_height) // 2
            img = img.crop((0, offset, img_width, img_height - offset))
        
        img = img.resize(output_size, Image.LANCZOS)
        
        # O MoviePy geralmente lida melhor com caminhos de arquivo do que objetos PIL diretamente para ImageClip
        # Então, salvamos a imagem processada e retornamos o caminho.
        base, ext = os.path.splitext(image_path)
        # Adicionar sufixo para evitar sobrescrever o original se o nome for o mesmo
        # e para facilitar a identificação de imagens processadas
        if not base.endswith("_processed"):
            processed_image_path = f"{base}_processed{ext}"
        else:
            processed_image_path = image_path # Já tem o sufixo (pode acontecer em re-processamento)
        
        img.save(processed_image_path)
        return processed_image_path
    except FileNotFoundError:
        logging.error(f"Arquivo de imagem não encontrado em resize_and_crop: {image_path}")
        return None
    except Exception as e:
        logging.error(f"Erro ao redimensionar/cortar imagem {image_path}: {e}")
        return None


def ken_burns_effect(clip, R_start=1.0, R_end=1.2, pos_start=('center', 'center'), pos_end=('center', 'center'), speed_factor=0.2):
    """
    Aplica um efeito Ken Burns (zoom e pan suaves) a um clipe de imagem.
    R_start, R_end: Fatores de zoom inicial e final.
    pos_start, pos_end: Posições iniciais e finais ('center', 'left', 'right', 'top', 'bottom').
    speed_factor: (não usado diretamente aqui, o efeito é sobre a duração do clipe)
    """
    def effect(get_frame, t):
        frame = get_frame(t)
        h, w = frame.shape[:2]
        
        progress_time = t / clip.duration
        progress = progress_time**2 * (3 - 2 * progress_time) # Ease-in-out

        R = R_start + (R_end - R_start) * progress
        
        def get_coords(pos_str, dim_size, zoomed_dim_size):
            if pos_str == 'center': return (dim_size - zoomed_dim_size) / 2
            if pos_str in ('left', 'top'): return 0
            if pos_str in ('right', 'bottom'): return dim_size - zoomed_dim_size
            return (dim_size - zoomed_dim_size) / 2 

        new_w, new_h = int(w / R), int(h / R)

        x_start_coord = get_coords(pos_start[0], w, new_w)
        x_end_coord = get_coords(pos_end[0], w, new_w)
        x = int(x_start_coord + (x_end_coord - x_start_coord) * progress)

        y_start_coord = get_coords(pos_start[1], h, new_h)
        y_end_coord = get_coords(pos_end[1], h, new_h)
        y = int(y_start_coord + (y_end_coord - y_start_coord) * progress)

        # Garantir que as coordenadas de corte não saiam dos limites
        x = max(0, min(x, w - new_w))
        y = max(0, min(y, h - new_h))
        
        sub_frame = frame[y:y+new_h, x:x+new_w]
        
        pil_img = Image.fromarray(sub_frame)
        pil_img_resized = pil_img.resize((w, h), Image.LANCZOS)
        return np.array(pil_img_resized)

    return clip.fl(effect, apply_to=['mask'] if clip.mask else [])