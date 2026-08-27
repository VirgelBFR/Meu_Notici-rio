"""
Mantém o feed RSS público do podcast (docs/feed.xml), que é hospedado pelo
GitHub Pages e usado pelo Spotify for Podcasters para puxar novos episódios
automaticamente.

Cada novo episódio:
1. É copiado para docs/audio/<slug>.mp3 (servido publicamente pelo GitHub Pages)
2. Vira uma entrada nova em data/episodes.json (nosso "banco de dados" simples)
3. O feed.xml inteiro é regenerado a partir de data/episodes.json

Depois de rodar, é só o GitHub Actions commitar e dar push nesses arquivos
(docs/feed.xml, docs/audio/*, data/episodes.json) — o workflow já faz isso.
"""

import json
import os
import shutil
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

# ==== PREENCHA COM OS DADOS DO SEU PODCAST ====
PODCAST_TITLE = "Nome do Seu Podcast"
PODCAST_DESCRIPTION = "Resumo diário das principais notícias, direto ao ponto."
PODCAST_LANGUAGE = "pt-br"
PODCAST_AUTHOR = "Seu Nome"
PODCAST_EMAIL = "seu-email@exemplo.com"
PODCAST_IMAGE_URL = "https://VirgelBFR.github.io/podcast-noticias/cover.jpg"
SITE_BASE_URL = "https://VirgelBFR.github.io/podcast-noticias"
# ===============================================

EPISODES_JSON = "data/episodes.json"
DOCS_DIR = "docs"
AUDIO_DIR = os.path.join(DOCS_DIR, "audio")
FEED_PATH = os.path.join(DOCS_DIR, "feed.xml")


def _load_episodes() -> list[dict]:
    if not os.path.exists(EPISODES_JSON):
        return []
    with open(EPISODES_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_episodes(episodes: list[dict]) -> None:
    os.makedirs(os.path.dirname(EPISODES_JSON), exist_ok=True)
    with open(EPISODES_JSON, "w", encoding="utf-8") as f:
        json.dump(episodes, f, ensure_ascii=False, indent=2)


def add_episode(mp3_path: str, title: str, description: str) -> dict:
    """Copia o MP3 para docs/audio/, registra o episódio e retorna seus metadados."""
    os.makedirs(AUDIO_DIR, exist_ok=True)

    now = datetime.now(timezone.utc)
    slug = now.strftime("%Y-%m-%d-%H%M")
    file_name = f"{slug}.mp3"
    dest_path = os.path.join(AUDIO_DIR, file_name)
    shutil.copyfile(mp3_path, dest_path)

    file_size = os.path.getsize(dest_path)

    episode = {
        "title": title,
        "description": description,
        "pub_date": now.isoformat(),
        "audio_url": f"{SITE_BASE_URL}/audio/{file_name}",
        "file_size_bytes": file_size,
        "guid": slug,
    }

    episodes = _load_episodes()
    episodes.insert(0, episode)  # mais recente primeiro
    _save_episodes(episodes)
    return episode


def _rfc2822(iso_date: str) -> str:
    return format_datetime(datetime.fromisoformat(iso_date))


def regenerate_feed() -> str:
    episodes = _load_episodes()

    items_xml = []
    for ep in episodes:
        items_xml.append(f"""
    <item>
      <title>{escape(ep['title'])}</title>
      <description>{escape(ep['description'])}</description>
      <pubDate>{_rfc2822(ep['pub_date'])}</pubDate>
      <enclosure url="{escape(ep['audio_url'])}" length="{ep['file_size_bytes']}" type="audio/mpeg" />
      <guid isPermaLink="false">{escape(ep['guid'])}</guid>
      <itunes:duration></itunes:duration>
    </item>""")

    feed_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>{escape(PODCAST_TITLE)}</title>
    <description>{escape(PODCAST_DESCRIPTION)}</description>
    <language>{PODCAST_LANGUAGE}</language>
    <link>{SITE_BASE_URL}</link>
    <itunes:author>{escape(PODCAST_AUTHOR)}</itunes:author>
    <itunes:owner>
      <itunes:name>{escape(PODCAST_AUTHOR)}</itunes:name>
      <itunes:email>{escape(PODCAST_EMAIL)}</itunes:email>
    </itunes:owner>
    <itunes:image href="{escape(PODCAST_IMAGE_URL)}" />
    <itunes:category text="News" />
    <itunes:explicit>false</itunes:explicit>
    <image>
      <url>{escape(PODCAST_IMAGE_URL)}</url>
      <title>{escape(PODCAST_TITLE)}</title>
      <link>{SITE_BASE_URL}</link>
    </image>
    {''.join(items_xml)}
  </channel>
</rss>
"""

    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(FEED_PATH, "w", encoding="utf-8") as f:
        f.write(feed_xml)

    return FEED_PATH


if __name__ == "__main__":
    add_episode("audio/episodio.mp3", "Episódio de teste", "Descrição de teste")
    path = regenerate_feed()
    print(f"Feed atualizado em: {path}")
