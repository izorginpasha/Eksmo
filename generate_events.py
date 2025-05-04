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
Ты — звуковой дизайнер. Проанализируй текст и верни список звуковых эффектов с их параметрами.
Формат строго такой:

[
  {{
    "sound": "название.wav",
    "start": 1.5,
    "duration": 2.0,
    "volume": -5
  }}
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

        match = re.search(r'\[(?:.|\n)*?\]', result)
        if match:
            return eval(match.group(0))
        return []
    except Exception as e:
        print("❌ Ошибка Ollama:", e)
        return []

def merge_segments(segments, max_duration=10.0):
    """Объединяет сегменты whisper в блоки до max_duration секунд"""
    merged = []
    buffer = []
    buffer_start = None

    for seg in segments:
        if not buffer:
            buffer_start = seg['start']
        buffer.append(seg)

        total_duration = seg['end'] - buffer_start
        if total_duration >= max_duration:
            merged.append({
                "start": buffer_start,
                "end": seg['end'],
                "text": " ".join(s['text'] for s in buffer)
            })
            buffer = []

    if buffer:
        merged.append({
            "start": buffer_start,
            "end": buffer[-1]['end'],
            "text": " ".join(s['text'] for s in buffer)
        })

    return merged

def main():
    audio_path = "audio/voice.mp3"
    result = model.transcribe(audio_path, language="ru", verbose=False)
    segments = result["segments"]

    # 🔁 Объединяем сегменты по 10 секунд
    merged_segments = merge_segments(segments, max_duration=10.0)

    events = []
    for seg in merged_segments:
        print(f"🗣️ Сегмент (объединённый): {seg['text']}")
        sfx_list = get_sfx_from_ollama(seg['text'])
        print(f"🎵 Найдено эффектов: {sfx_list}")
        for sfx in sfx_list:
            events.append({
                "text": seg['text'],
                "sound": sfx["sound"],
                "start": seg["start"] + float(sfx["start"]),  # смещение внутри объединённого блока
                "duration": float(sfx["duration"]),
                "volume": float(sfx["volume"])
            })

    save_events_to_excel(events)

if __name__ == "__main__":
    main()