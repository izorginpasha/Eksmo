import whisper
import spacy
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import normalize
import os
from pathlib import Path

# Загружаем модель распознавания речи
model = whisper.load_model("base")
nlp = spacy.load("ru_core_news_sm")

#-------------Имитация озвучки диктора--------
# #Путь к тексту
# with open("text_file/text.txt", "r", encoding="utf-8") as f:
#     text = f.read()

#Озвучка текста через gTTS
# tts = gTTS(text, lang='ru')
# tts.save("audio/voice.mp3")
# ---------------------------------------------
# ------------------- Функция вызова LLM через Ollama -------------------
def get_sfx_from_ollama(text_segment):
    prompt = f"""
Ты — звуковой дизайнер.
На основе текста верни подходящие звуки в формате Python-списка (только имена файлов, ничего лишнего).
Текст: "{text_segment}"
"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": False}
        )
        return eval(response.json()['response'].strip())
    except Exception as e:
        print("❌ Ошибка Ollama:", e)
        return []

# ------------------- Основные функции -------------------

def final_mix(voice, fx_track):
    final = voice.overlay(fx_track)
    final.export("result.wav", format="wav")
    print("✅ Готово: result.wav")

def time_based_effects(events, fx_dir, voice):
    fx_track = AudioSegment.silent(duration=len(voice))
    for event in events:
        fx_path = fx_dir / event["sound"]
        if fx_path.exists():
            fx = AudioSegment.from_wav(fx_path).fade_in(300).fade_out(500) - 10
            fx_track = fx_track.overlay(fx, position=event["position"])
        else:
            print(f"⚠️ Звук не найден: {fx_path}")
    final_mix(voice, fx_track)

def transcribe_and_analyze(audio_path, fx_dir):
    voice = AudioSegment.from_mp3(audio_path)
    result = model.transcribe(audio_path, language="ru", verbose=False)
    segments = result['segments']

    keywords = {
        "разговор": "crowd_talk.wav",
        "волна": "sea_waves.wav",
        "скрежет": "metal_scrape.wav",
        "чайка": "seagulls.wav",
        "топот": "footsteps.wav",
        "ветер": "wind.wav",
        "скрип": "wooden_creak.wav",
        "эхо": "metal_echo_step.wav"
    }

    events = []
    for seg in segments:
        for key, fx in keywords.items():
            if key in seg['text'].lower():
                events.append({
                    "text": seg['text'],
                    "sound": fx,
                    "position": int(seg['start'] * 1000)
                })

    time_based_effects(events, fx_dir, voice)

# ------------------- Точка входа -------------------

def main():
    fx_dir = Path("audio/fx")
    audio_path = "audio/voice.mp3"
    transcribe_and_analyze(audio_path, fx_dir)

if __name__ == "__main__":
    main()