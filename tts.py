"""
Converte o roteiro do podcast (lista de falas) em um único arquivo MP3,
usando o edge-tts — biblioteca gratuita que usa as vozes neurais do
Microsoft Edge (não precisa de conta nem chave de API).

Vozes em português do Brasil disponíveis: "pt-BR-FranciscaNeural" (feminina)
e "pt-BR-AntonioNeural" (masculina). Para ver a lista completa, rode:
    edge-tts --list-voices | grep pt-BR
"""

import asyncio
import os

import edge_tts
from pydub import AudioSegment

VOICE_MAP = {
    "Ana": os.environ.get("EDGE_TTS_VOICE_ANA", "pt-BR-FranciscaNeural"),
    "Bruno": os.environ.get("EDGE_TTS_VOICE_BRUNO", "pt-BR-AntonioNeural"),
}


async def _synthesize_line(text: str, voice: str, out_path: str) -> None:
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out_path)


def build_podcast_audio(script: list[dict], output_path: str = "audio/episodio.mp3") -> str:
    for speaker, voice in VOICE_MAP.items():
        if not voice:
            raise ValueError(f"Voz do edge-tts não configurada para '{speaker}'.")

    combined = AudioSegment.silent(duration=300)  # pequeno silêncio inicial
    pause = AudioSegment.silent(duration=350)      # pausa natural entre falas

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    tmp_path = output_path + ".part.mp3"

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        for i, line in enumerate(script):
            speaker = line["speaker"]
            voice = VOICE_MAP.get(speaker)
            if not voice:
                raise ValueError(f"Jornalista desconhecido no roteiro: {speaker}")

            loop.run_until_complete(_synthesize_line(line["text"], voice, tmp_path))
            segment = AudioSegment.from_mp3(tmp_path)
            combined += segment + pause
            print(f"[{i+1}/{len(script)}] áudio gerado para {speaker}")
    finally:
        loop.close()

    if os.path.exists(tmp_path):
        os.remove(tmp_path)

    combined.export(output_path, format="mp3", bitrate="128k")
    return output_path


if __name__ == "__main__":
    import json

    with open("data/ultimo_roteiro.json", "r", encoding="utf-8") as f:
        script = json.load(f)

    path = build_podcast_audio(script)
    print(f"Áudio salvo em: {path}")
