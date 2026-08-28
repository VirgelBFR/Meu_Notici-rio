"""
Faz upload do episódio MP3 para uma pasta específica no Google Drive,
autenticando como VOCÊ MESMO (via OAuth), em vez de uma service account.

Motivo: contas de serviço não têm espaço de armazenamento próprio no
Google Drive, então uploads por elas falham com "storageQuotaExceeded"
mesmo enviando para uma pasta compartilhada. Usando OAuth com sua própria
conta, os arquivos contam no seu espaço normal do Drive (15GB grátis).

Requer as variáveis de ambiente (geradas uma única vez com oauth_setup.py,
rodado localmente — veja o README):
- GOOGLE_OAUTH_CLIENT_ID
- GOOGLE_OAUTH_CLIENT_SECRET
- GOOGLE_OAUTH_REFRESH_TOKEN
- GOOGLE_DRIVE_FOLDER_ID
"""

import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN_URI = "https://oauth2.googleapis.com/token"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _get_drive_service():
    credentials = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_OAUTH_REFRESH_TOKEN"],
        token_uri=TOKEN_URI,
        client_id=os.environ["GOOGLE_OAUTH_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_OAUTH_CLIENT_SECRET"],
        scopes=SCOPES,
    )
    return build("drive", "v3", credentials=credentials)


def upload_episode(file_path: str, file_name: str | None = None) -> str:
    folder_id = os.environ["GOOGLE_DRIVE_FOLDER_ID"]
    service = _get_drive_service()

    file_name = file_name or os.path.basename(file_path)
    metadata = {"name": file_name, "parents": [folder_id]}
    media = MediaFileUpload(file_path, mimetype="audio/mpeg", resumable=True)

    uploaded = service.files().create(
        body=metadata, media_body=media, fields="id, webViewLink"
    ).execute()

    print(f"Upload concluído: {uploaded.get('webViewLink')}")
    return uploaded["id"]


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "audio/episodio.mp3"
    upload_episode(path)
