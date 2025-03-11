from moviepy.editor import *
from moviepy.video.fx import all as vfx
import requests
from PIL import Image
from io import BytesIO
import logging
import os
import numpy as np
from vidgear.gears import CamGear
from vidgear.gears import WriteGear

from src.config import IMAGES_DIR, VIDEOS_DIR

def resize_image_to_16_9(image_path, output_path):
    """
    Redimensiona uma imagem para o formato 16:9 (1920x1080).
    """
    img = Image.open(image_path)
    original_width, original_height = img.size

    # Calcula a proporção para manter a imagem centralizada
    aspect_ratio = 16 / 9
    if original_width / original_height > aspect_ratio:
        # A imagem é mais larga que 16:9, corta as bordas laterais
        new_width = int(original_height * aspect_ratio)
        left = (original_width - new_width) // 2
        right = left + new_width
        cropped_img = img.crop((left, 0, right, original_height))
    else:
        # A imagem é mais alta que 16:9, corta as bordas superior/inferior
        new_height = int(original_width / aspect_ratio)
        top = (original_height - new_height) // 2
        bottom = top + new_height
        cropped_img = img.crop((0, top, original_width, bottom))

    # Redimensiona para 1920x1080
    resized_img = cropped_img.resize((1920, 1080), Image.LANCZOS)
    resized_img.save(output_path)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_video(audio_file, image_urls, output_file):
    logging.info("Iniciando a criação do vídeo...")
    clips = []
    try:
        audio = AudioFileClip(audio_file)
        total_duration = audio.duration
        current_time = 0
        logging.info(f"Duração total do áudio: {total_duration} segundos")
    except Exception as e:
        logging.error(f"Erro ao carregar o arquivo de áudio: {e}", exc_info=True)
        raise

    logging.info("Garantindo que haja pelo menos uma imagem válida...")
    # Garantir que haja pelo menos uma imagem válida
    if not image_urls:
        print("Nenhuma imagem válida encontrada. Usando imagem padrão.")
        default_image = "https://via.placeholder.com/1920x1080"
        image_urls = [default_image]
    logging.info(f"Lista de imagens: {image_urls}")

    logging.info("Iniciando o loop de criação de clipes...")
    # Rotacionar entre as imagens disponíveis
    while current_time < total_duration:
        for i, url in enumerate(image_urls):
            logging.info(f"Processando imagem {i+1}/{len(image_urls)}: {url}")
            try:
                # Baixar a imagem
                logging.info("Baixando a imagem...")
                response = requests.get(url, timeout=10)
                if response.status_code != 200:
                    logging.warning(f"Falha ao baixar a imagem. Status code: {response.status_code}")
                    continue

                # Salvar a imagem temporariamente
                logging.info("Salvando a imagem temporariamente...")
                temp_image_path = f"{IMAGES_DIR}/temp_image_{i}.jpg"
                with open(temp_image_path, "wb") as img_file:
                    img_file.write(response.content)

                # Redimensionar para 16:9
                logging.info("Redimensionando a imagem para 16:9...")
                resized_image_path = f"{IMAGES_DIR}/resized_image_{i}.jpg"
                resize_image_to_16_9(temp_image_path, resized_image_path)

                # Criar clipe de imagem com duração de 4 segundos
                logging.info("Criando clipe de imagem...")
                #clip = ImageClip(resized_image_path, duration=4)

                # Load image with PIL
                img = Image.open(resized_image_path)
                # Convert to numpy array
                img_array = np.array(img)

                # Add zoom effect
                zoom_factor = 1.1
                h, w = img_array.shape[:2]
                zh = int(h / zoom_factor)
                zw = int(w / zoom_factor)
                top = (h - zh) // 2
                left = (w - zw) // 2
                img_array = img_array[top:top+zh, left:left+zw]
                img_array = Image.fromarray(img_array).resize((w, h))
                img_array = np.array(img_array)

                clip = ImageClip(img_array, duration=4)

                clips.append(clip.set_start(current_time))
                current_time += 4

                # Limpar arquivos temporários
                logging.info("Limpando arquivos temporários...")
                os.remove(temp_image_path)

                # Parar se o tempo total for atingido
                if current_time >= total_duration:
                    logging.info("Tempo total atingido. Saindo do loop.")
                    break
            except Exception as e:
                print(f"Erro ao processar imagem {url}: {e}")
                # Log the error and continue with the next image
                logging.error(f"Erro ao processar imagem {url}: {e}", exc_info=True)
                continue

    # Concatenar todos os clipes de imagem
    if not clips:
        raise ValueError("Nenhuma imagem válida foi processada.")

    # Add fade transition between clips
    for i in range(len(clips) - 1):
        clips[i] = clips[i].crossfadein(1.0)

    final_clip = concatenate_videoclips(clips, method="compose")

    # Definir o áudio no vídeo
    final_clip = final_clip.set_audio(audio)

    # Garantir que o vídeo tenha a mesma duração do áudio
    if final_clip.duration < total_duration:
        last_clip = clips[-1]
        remaining_time = total_duration - final_clip.duration
        repeated_clip = last_clip.fx(vfx.loop, duration=remaining_time).set_start(final_clip.duration)
        final_clip = concatenate_videoclips([final_clip, repeated_clip])

    # Exportar o vídeo final
    final_clip.write_videofile(output_file, fps=24)
    print(f"Vídeo gerado com sucesso: {output_file}")
    logging.info(f"Vídeo gerado com sucesso: {output_file}")
