import whisper
import requests
from pathlib import Path
import pandas as pd
import re
from utilities.utilities import save_events_to_excel

# Загружаем модель
model = whisper.load_model("medium")

def get_sfx_from_ollama(text_segment):
    fx_dir = Path("audio/fx")
    available_sounds = {p.name for p in fx_dir.glob("*.wav")}
    sound_list = "\n".join(f'- {s}' for s in sorted(available_sounds))
    prompt = f"""
    Ты — звуковой дизайнер. У тебя есть список доступных звуковых эффектов:

    {sound_list}

    Проанализируй текст и определи, какие звуковые эффекты ярко выражены и  подойдут.
    Если подходящий звук уже есть в списке — используй его.
    Если в списке нет нужного — придумай новое имя в формате `название.wav`.

    Формат ответа строго такой:

     [
      {{
        "sound": "название.wav",
        "volume": -5,
        "pan": 0.0,
        "background_noise": "название.wav"
      }}
    ]


    Только JSON. Без пояснений. Текст: \"\"\"{text_segment}\"\"\"
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False}
        )
        result = response.json().get("response", "").strip()
        print("📤 Ответ от Ollama:", repr(result))

        match = re.search(r'\[(?:.|\n)*?\]', result)
        if match:
            return eval(match.group(0))
        return []
    except Exception as e:
        print("❌ Ошибка Ollama:", e)
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
                "sound": sfx["sound"],
                "volume": float(sfx.get("volume", 0)),
                "pan": float(sfx.get("pan", 0.0)),
                "background_noise": sfx.get("background_noise", "")
            })

    save_events_to_excel(events)

if __name__ == "__main__":
    main()
