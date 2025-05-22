from gtts import gTTS
# from src.config import AUDIO_DIR # AUDIO_DIR não é usado aqui, o path completo é passado
import logging

# Se o logging já está configurado no app.py ou main.py, esta linha pode não ser necessária
# ou pode ser configurada para obter o logger raiz.
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # Boa prática usar logger específico do módulo

def text_to_speech(text, output_file, lang='en'): # Adicionado 'lang' como parâmetro
    logger.info(f"Iniciando a geração do áudio para: {output_file}")
    try:
        # Criar áudio usando gTTS
        # logger.debug(f"Texto a ser convertido: {text[:100]}...") # Logar apenas uma parte
        tts = gTTS(text=text, lang=lang, slow=False)
        # logger.info("Objeto gTTS criado com sucesso.")
        tts.save(output_file)
        logger.info(f"Áudio gerado com sucesso: {output_file}")
        # print(f"Áudio gerado com sucesso: {output_file}") # 'print' é mais para CLI, logging é melhor
    except Exception as e:
        logger.error(f"Erro ao gerar áudio com gTTS: {e}", exc_info=True)
        # print(f"Erro ao gerar áudio: {e}")
        raise # Relançar a exceção para que o chamador possa lidar com ela