import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Escopo necessário para upload de vídeos no YouTube
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    creds = None
    # O arquivo token.pickle armazena o acesso do usuário e atualiza tokens
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # Se não houver credenciais válidas, faça o login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Certifique-se de que o arquivo client_secrets.json existe
            if not os.path.exists("client_secrets.json"):
                raise FileNotFoundError("Arquivo 'client_secrets.json' não encontrado. Baixe as credenciais OAuth2 no Google Cloud Console.")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Salve as credenciais para a próxima execução
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build("youtube", "v3", credentials=creds)

def upload_to_youtube(video_file, title, description):
    youtube = get_authenticated_service()
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["Bitcoin", "Notícias"],
                "categoryId": "25"  # Categoria Notícias
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload(video_file)
    )
    response = request.execute()
    return response