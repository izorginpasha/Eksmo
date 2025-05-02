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
#Путь к тексту
with open("text_file/text.txt", "r", encoding="utf-8") as f:
    text = f.read()

#Озвучка текста через gTTS
# tts = gTTS(text, lang='ru')
# tts.save("audio/voice.mp3")
# ---------------------------------------------




# ------------Пути
voice = AudioSegment.from_mp3("audio/voice.mp3")
duration = len(voice)
fx_dir = Path("audio/fx")
fx_track = AudioSegment.silent(duration=duration)

# Шаг 1. Распознаём речь и получаем таймкоды:
result = model.transcribe("audio/voice.mp3", language="ru", verbose=False)
segments = result['segments']  # список сегментов с текстом и временем


events = []
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

# Шаг 2. Сопоставляем события с фразами

for seg in segments:
    for key, fx in keywords.items():
        if key in seg['text'].lower():
            events.append({
                "text": seg['text'],
                "sound": fx,
                "position": int(seg['start'] * 1000)  # в миллисекундах
            })
 # Шаг 3. Вставляем эффекты точно по времени:
for event in events:
    fx_path = fx_dir / event["sound"]
    if fx_path.exists():
        fx = AudioSegment.from_wav(fx_path).fade_in(300).fade_out(500) - 10
        fx_track = fx_track.overlay(fx, position=event["position"])
    else:
        print(f"⚠️ Звук не найден: {fx_path}")
#
# # Шаг 4. Финальный микс
final = voice.overlay(fx_track)
final.export("result.wav", format="wav")
print("✅ Готово: result.wav")
