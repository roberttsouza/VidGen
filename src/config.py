import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações da API
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_CLIENT_ID = os.getenv('YOUTUBE_CLIENT_ID')
YOUTUBE_CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET')

UNSPLASH_APPLICATION_ID = os.getenv('UNSPLASH_APPLICATION_ID')
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')
UNSPLASH_SECRET_KEY = os.getenv('UNSPLASH_SECRET_KEY')

# Diretórios do projeto
DATA_DIR = os.path.join(os.getcwd(), 'data')
AUDIO_DIR = os.path.join(DATA_DIR, 'audio')
IMAGES_DIR = os.path.join(DATA_DIR, 'images')
VIDEOS_DIR = os.path.join(DATA_DIR, 'videos')

# Criar diretórios se não existirem
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)


GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')