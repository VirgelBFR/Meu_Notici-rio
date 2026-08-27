"""
Orquestra o pipeline completo do podcast de notícias:

1. Coleta notícias recentes dos feeds RSS (feeds.txt)
2. Gera o roteiro de bate-papo entre dois jornalistas (Claude)
3. Sintetiza o áudio MP3 (ElevenLabs)
4. Salva o MP3 no Google Drive
5. Atualiza o feed RSS do podcast (docs/feed.xml) para o Spotify puxar

Uso: python main.py
"""

import json
import os
from datetime import date

from fetch_news import load_feed_urls, fetch_recent_news
from generate_script import generate_podcast_script
from tts import build_podcast_audio
from upload_drive import upload_episode
from update_feed import add_episode, regenerate_feed


def main():
    today = date.today().strftime("%d/%m/%Y")

    print("1/5 — Coletando notícias...")
    feed_urls = load_feed_urls()
    news = fetch_recent_news(feed_urls)
    print(f"   {len(news)} notícias coletadas de {len(feed_urls)} feeds.")

    if not news:
        print("Nenhuma notícia nova encontrada. Encerrando sem gerar episódio.")
        return

    print("2/5 — Gerando roteiro do podcast...")
    script = generate_podcast_script(news)

    os.makedirs("data", exist_ok=True)
    with open("data/ultimo_roteiro.json", "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)

    print("3/5 — Gerando áudio (isso pode levar alguns minutos)...")
    mp3_path = build_podcast_audio(script, output_path="audio/episodio.mp3")
    print(f"   Áudio salvo em: {mp3_path}")

    print("4/5 — Enviando para o Google Drive...")
    upload_episode(mp3_path, file_name=f"podcast-{date.today().isoformat()}.mp3")

    print("5/5 — Atualizando feed RSS do podcast (Spotify)...")
    episode_title = f"Notícias de {today}"
    episode_description = (
        f"Resumo em bate-papo das principais notícias de {today}, "
        f"com base em {len(news)} matérias de {len(feed_urls)} fontes."
    )
    add_episode(mp3_path, episode_title, episode_description)
    feed_path = regenerate_feed()
    print(f"   Feed atualizado em: {feed_path}")

    print("\nPronto! Depois que o GitHub Actions fizer o commit/push, "
          "o Spotify vai puxar o novo episódio automaticamente.")


if __name__ == "__main__":
    main()
