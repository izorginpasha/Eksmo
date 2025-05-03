import whisper
import requests
from pathlib import Path
import pandas as pd
from pydub import AudioSegment

# Загружаем модель
model = whisper.load_model("base")

def get_sfx_from_ollama(text_segment):
    prompt = f"""
    Ты — звуковой дизайнер.
    На основе текста подбери только список звуковых эффектов. Верни строго список строк в формате Python, без пояснений.
    Пример ответа: ["sound1.wav", "sound2.wav"]
    Текст: "{text_segment}"
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

def save_events_to_excel(events, output_path="events.xlsx"):
    if not events:
        print("⚠️ Нет событий для сохранения.")
        return
    df = pd.DataFrame(events)
    df["time_sec"] = df["position"] / 1000
    df = df[["text", "sound", "position", "time_sec"]]
    df.to_excel(output_path, index=False)
    print(f"✅ События сохранены в {output_path}")

def main():
    audio_path = "audio/voice.mp3"
    result = model.transcribe(audio_path, language="ru", verbose=False)
    segments = result["segments"]

    events = []
    for seg in segments:
        print(f"🗣️ Сегмент: {seg['text']}")
        sfx_list = get_sfx_from_ollama(seg['text'])
        print(f"🎵 Найдено эффектов: {sfx_list}")
        for sound_file in sfx_list:
            events.append({
                "text": seg['text'],
                "sound": sound_file,
                "position": int(seg['start'] * 1000)
            })

    save_events_to_excel(events)

if __name__ == "__main__":
    main()
