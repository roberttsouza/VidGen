from gtts import gTTS
from src.config import AUDIO_DIR

import logging

def text_to_speech(text, output_file):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Iniciando a geração do áudio...")
    try:
        # Criar áudio usando gTTS
        logging.info(f"Texto a ser convertido: {text}")
        tts = gTTS(text=text, lang='en', slow=False)
        logging.info("Objeto gTTS criado com sucesso.")
        tts.save(output_file)
        logging.info(f"Áudio gerado com sucesso: {output_file}")
        print(f"Áudio gerado com sucesso: {output_file}")
    except Exception as e:
        logging.error(f"Erro ao gerar áudio: {e}", exc_info=True)
        print(f"Erro ao gerar áudio: {e}")
