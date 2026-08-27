"""
Usa a API do Google Gemini (camada gratuita) para transformar a lista de
notícias coletadas num roteiro de podcast: um bate-papo natural entre
dois jornalistas.

Saída: lista de falas no formato [{"speaker": "Ana", "text": "..."}, ...]
para facilitar o envio linha a linha ao TTS (cada fala pode usar uma voz).
"""

import json
import os
from google import genai

# Modelo gratuito no Gemini API (camada free). Se o Google aposentar este
# modelo, troque por outro "flash"/"flash-lite" atual — confira em
# ai.google.dev/gemini-api/docs/models qual está disponível na camada grátis.
MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """\
Você é um roteirista de podcast de notícias brasileiro. Sua tarefa é pegar uma
lista de notícias (título, resumo, fonte) e transformar em um roteiro de
bate-papo natural, dinâmico e informativo entre dois jornalistas fictícios:
Ana e Bruno.

Regras:
- Comece com uma saudação curta de abertura do programa.
- Cubra as notícias mais relevantes agrupadas por tema (política, economia,
  tecnologia, etc.), com transições naturais entre os blocos.
- Os jornalistas devem comentar, contextualizar e, quando fizer sentido,
  discordar ou trazer nuances — não apenas ler a notícia em voz alta.
- Tom: informativo mas leve, como um podcast de notícias diário.
- Termine com um encerramento curto e convite para o próximo episódio.
- Duração alvo: equivalente a uns 6-10 minutos falados (aproximadamente
  900 a 1400 palavras no total).
- Responda APENAS com um JSON válido, sem markdown, sem texto fora do JSON,
  no formato:
  [{"speaker": "Ana", "text": "..."}, {"speaker": "Bruno", "text": "..."}, ...]
"""


def build_news_block(news: list[dict]) -> str:
    lines = []
    for n in news:
        lines.append(f"- [{n['source']}] {n['title']}: {n['summary']}")
    return "\n".join(lines)


def generate_podcast_script(news: list[dict]) -> list[dict]:
    if not news:
        raise ValueError("Nenhuma notícia recebida para gerar o roteiro.")

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    news_block = build_news_block(news)
    user_prompt = f"Notícias de hoje:\n\n{news_block}\n\nGere o roteiro do podcast."

    response = client.models.generate_content(
        model=MODEL,
        contents=user_prompt,
        config={
            "system_instruction": SYSTEM_PROMPT,
            "response_mime_type": "application/json",
        },
    )

    raw_text = response.text.strip()

    # remove eventuais cercas de markdown, caso o modelo insista em usá-las
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        raw_text = raw_text.split("\n", 1)[1] if "\n" in raw_text else raw_text
        if raw_text.lower().startswith("json"):
            raw_text = raw_text[4:].strip()

    script = json.loads(raw_text)
    return script


if __name__ == "__main__":
    from fetch_news import load_feed_urls, fetch_recent_news

    news = fetch_recent_news(load_feed_urls())
    script = generate_podcast_script(news)
    for line in script:
        print(f"{line['speaker']}: {line['text'][:80]}...")
