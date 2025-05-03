
import whisper
import spacy
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import normalize
import os
from pathlib import Path
import requests
from utilities.utilities import save_events_to_excel, mitation_acting

# Загружаем модель распознавания речи
model = whisper.load_model("base")
#-------------Имитация озвучки диктора - -------
#mitation_acting()


# ---------------------------------------------
# 🔁 Функция запроса в LLM
def get_sfx_from_ollama(text_segment):
    prompt = f"""
    Ты — звуковой дизайнер.

    На основе текста подбери только список звуковых эффектов. Верни строго список строк в формате Python, без пояснений.

    Пример ответа:
    ["sound1.wav", "sound2.wav"]

    Текст: "{text_segment}"
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": False}
        )
        result = response.json()['response']
        print("📤 Ответ от Ollama:", repr(result))
        return eval(result.strip()) if result.strip().startswith("[") else []

    except Exception as e:
        print("❌ Ошибка Ollama:", e)
        return []

# 🎧 Основной микширование эффектов
def mix_effects(audio_path, fx_dir):
    voice = AudioSegment.from_mp3(audio_path)
    duration = len(voice)
    fx_track = AudioSegment.silent(duration=duration)

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

    for event in events:
        fx_path = fx_dir / event["sound"]
        if fx_path.exists():
            fx = AudioSegment.from_wav(fx_path).fade_in(300).fade_out(500) - 10
            fx_track = fx_track.overlay(fx, position=event["position"])
        else:
            print(f"⚠️ Не найден звук: {fx_path}")

    final = voice.overlay(fx_track)
    final.export("result.wav", format="wav")
    print("✅ Финальный файл сохранён: result.wav")
    save_events_to_excel(events)

# 🚀 Точка входа
def main():
    audio_path = "audio/voice.mp3"
    fx_dir = Path("audio/fx")
    mix_effects(audio_path, fx_dir)

if __name__ == "__main__":
    main()