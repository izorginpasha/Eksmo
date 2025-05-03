import whisper
import requests
from pathlib import Path
import pandas as pd
from pydub import AudioSegment
from utilities.utilities import save_events_to_excel
# Загружаем модель
model = whisper.load_model("medium")

def get_sfx_from_ollama(text_segment):
    prompt = f"""
    Ты — звуковой дизайнер. Проанализируй текст и верни список звуковых эффектов с их параметрами.
    Формат строго такой:

    [
      {{
        "sound": "название.wav",
        "start": 1.5,
        "duration": 2.0,
        "volume": -5
      }},
      ...
    ]

    Только JSON, никаких пояснений. Текст: \"\"\"{text_segment}\"\"\"
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": False}
        )
        result = response.json().get("response", "").strip()
        print("📤 Ответ от Ollama:", repr(result))

        import re
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
        print(f"🗣️ Сегмент: {seg['text']}")
        sfx_list = get_sfx_from_ollama(seg['text'])
        print(f"🎵 Найдено эффектов: {sfx_list}")
        for sfx in sfx_list:
            events.append({
                "text": seg['text'],
                "sound": sfx["sound"],
                "start": float(sfx["start"]),
                "duration": float(sfx["duration"]),
                "volume": float(sfx["volume"])
            })

    save_events_to_excel(events)

if __name__ == "__main__":
    main()
