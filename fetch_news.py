"""
Coleta as notícias mais recentes de uma lista de feeds RSS.

Lê o arquivo feeds.txt (um link por linha, '#' comenta a linha) e retorna
uma lista de notícias publicadas nas últimas HOURS_WINDOW horas, com
título, resumo e link, agrupadas por feed de origem.
"""

import feedparser
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser

HOURS_WINDOW = 24          # janela de tempo: só pega notícias das últimas 24h
MAX_PER_FEED = 8           # limite de notícias por feed, para não estourar o roteiro


def load_feed_urls(path: str = "feeds.txt") -> list[str]:
    urls = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def _parse_date(entry) -> datetime | None:
    # feedparser normaliza data em published_parsed quando consegue;
    # fallback para o campo de texto cru se precisar.
    if getattr(entry, "published_parsed", None):
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    if getattr(entry, "published", None):
        try:
            return date_parser.parse(entry.published).astimezone(timezone.utc)
        except (ValueError, TypeError):
            return None
    return None


def fetch_recent_news(feed_urls: list[str], hours_window: int = HOURS_WINDOW) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_window)
    all_news = []

    for url in feed_urls:
        parsed = feedparser.parse(url)
        if parsed.bozo and not parsed.entries:
            print(f"[aviso] não consegui ler o feed: {url}")
            continue

        source_name = parsed.feed.get("title", url)
        count = 0
        for entry in parsed.entries:
            if count >= MAX_PER_FEED:
                break

            pub_date = _parse_date(entry)
            if pub_date and pub_date < cutoff:
                continue  # notícia velha, pula

            all_news.append({
                "source": source_name,
                "title": entry.get("title", "").strip(),
                "summary": entry.get("summary", entry.get("description", "")).strip(),
                "link": entry.get("link", ""),
                "published": pub_date.isoformat() if pub_date else None,
            })
            count += 1

    return all_news


if __name__ == "__main__":
    feeds = load_feed_urls()
    news = fetch_recent_news(feeds)
    print(f"{len(news)} notícias coletadas de {len(feeds)} feeds.")
    for n in news:
        print(f"- [{n['source']}] {n['title']}")
