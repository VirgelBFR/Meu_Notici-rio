"""
Faz upload do episódio MP3 para uma pasta específica no Google Drive,
usando uma Service Account (sem interação humana necessária).

Requer:
- Variável de ambiente GOOGLE_SERVICE_ACCOUNT_JSON: conteúdo (texto) do
  arquivo JSON de credenciais da service account.
- Variável de ambiente GOOGLE_DRIVE_FOLDER_ID: ID da pasta de destino no
  Drive (pegue na URL da pasta) — a pasta deve ser compartilhada com o
  e-mail da service account (campo "client_email" no JSON).
"""

import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _get_drive_service():
    creds_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    credentials = service_account.Credentials.from_service_account_info(
        creds_info, scopes=SCOPES
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
