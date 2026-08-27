"""
Usa a API do Google Gemini (camada gratuita) para transformar a lista de
notícias coletadas num roteiro de podcast: um boletim narrado por um único
apresentador (formato ajustado ao gTTS, que só oferece uma voz).

Saída: lista de blocos no formato [{"speaker": "Apresentador", "text": "..."}, ...]
(um bloco por tema/notícia), para facilitar o envio ao TTS em partes.
"""

import json
import os
from google import genai

# Modelo gratuito no Gemini API (camada free). Se o Google aposentar este
# modelo, troque por outro "flash"/"flash-lite" atual — confira em
# ai.google.dev/gemini-api/docs/models qual está disponível na camada grátis.
MODEL = "gemini-3.6-flash"

SYSTEM_PROMPT = """\
Você é um roteirista de podcast de notícias brasileiro. Sua tarefa é pegar uma
lista de notícias (título, resumo, fonte) e transformar em um roteiro de
boletim narrado por um único apresentador, em tom natural e informativo —
como um noticiário de rádio matinal.

Regras:
- Comece com uma saudação curta de abertura do programa.
- Cubra as notícias mais relevantes agrupadas por tema (política, economia,
  tecnologia, etc.), com transições naturais entre os blocos.
- Não apenas leia a notícia: contextualize, explique o porquê de importar,
  traga uma pitada de análise quando fizer sentido.
- Tom: informativo mas leve, como um podcast de notícias diário.
- Termine com um encerramento curto e convite para o próximo episódio.
- Duração alvo: equivalente a uns 6-10 minutos falados (aproximadamente
  900 a 1400 palavras no total).
- Responda APENAS com um JSON válido, sem markdown, sem texto fora do JSON,
  no formato (todo bloco usa sempre "speaker": "Apresentador"):
  [{"speaker": "Apresentador", "text": "..."}, {"speaker": "Apresentador", "text": "..."}, ...]
  Divida o texto em vários blocos (um por bloco temático) em vez de um bloco
  único gigante — isso ajuda a geração do áudio.
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
