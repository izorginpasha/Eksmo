import whisper
import requests
from pathlib import Path
import pandas as pd
import re
from utilities.utilities import save_events_to_excel

# Загружаем модель
model = whisper.load_model("medium")


def get_sfx_from_ollama(text_segment):

    prompt = f"""
    Ты — звуковой дизайнер.

    Проанализируй текст и определи, какие звуковые эффекты ярко выражены и  подойдут.
    Придумай имя звука  в формате `название.wav`.

    Формат ответа строго такой:

     [
      {{
        "background_noise": "название.wav",
        "volume": -5,
        "pan": 0.0,
      }}
    ]


    Только JSON. Без пояснений. Текст: \"\"\"{text_segment}\"\"\"
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "qwen2:1.5b-instruct", "prompt": prompt, "stream": False}
        )
        result = response.json().get("response", "").strip()
        print("📤 Ответ от модели:", repr(result))

        match = re.search(r'\[(?:.|\n)*?\]', result)
        if match:
            return eval(match.group(0))
        return []
    except Exception as e:
        print("❌ Ошибка модели:", e)
        return []

def main():
    audio_path = "audio/voice.mp3"
    result = model.transcribe(audio_path, language="ru", verbose=False)
    segments = result["segments"]

    events = []
    for seg in segments:
        if seg["no_speech_prob"] < 0.5 and seg["avg_logprob"] > -1.0 and seg["compression_ratio"] < 2.4:
            print("✅ Сегмент принят:", seg["text"])
        else:
            print("⚠️ Сегмент отклонён:", seg["text"])
            continue

        sfx_list = get_sfx_from_ollama(seg['text'])
        print(f"🎵 Найдено эффектов: {sfx_list}")
        for sfx in sfx_list:
            events.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"],
                "background_noise": sfx["background_noise"],
                "volume": float(sfx.get("volume", 0)),
                "pan": float(sfx.get("pan", 0.0)),

            })

    save_events_to_excel(events)

if __name__ == "__main__":
    main()
