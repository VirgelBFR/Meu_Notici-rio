"""
Converte o roteiro do podcast (lista de falas) em um único arquivo MP3,
usando o gTTS (biblioteca gratuita que usa o motor de voz do Google
Tradutor). Não precisa de conta, chave de API nem cartão de crédito.

Limitação: o gTTS não oferece vozes diferentes por gênero/pessoa como o
Polly ou o Google Cloud TTS — é uma voz só em português. Os dois
jornalistas vão soar parecidos (o roteiro continua diferenciando quem
fala, só que na mesma voz). Se um dia quiser vozes diferentes de graça,
seria necessário voltar a usar um serviço com conta na nuvem.
"""

import os

from gtts import gTTS
from pydub import AudioSegment

# tld muda sutilmente o sotaque/entonação (mesma voz-base). Deixe como está
# a menos que queira experimentar variações.
TLD = "com.br"


def build_podcast_audio(script: list[dict], output_path: str = "audio/episodio.mp3") -> str:
    combined = AudioSegment.silent(duration=300)  # pequeno silêncio inicial
    pause = AudioSegment.silent(duration=350)      # pausa natural entre falas

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    tmp_path = output_path + ".part.mp3"

    for i, line in enumerate(script):
        speaker = line["speaker"]
        text = line["text"]

        tts = gTTS(text=text, lang="pt", tld=TLD)
        tts.save(tmp_path)

        segment = AudioSegment.from_mp3(tmp_path)
        combined += segment + pause
        print(f"[{i+1}/{len(script)}] áudio gerado para {speaker}")

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
