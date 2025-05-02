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
# Путь к тексту
# with open("text_file/text.txt", "r", encoding="utf-8") as f:
#     text = f.read()

# Озвучка текста через gTTS
# tts = gTTS(text, lang='ru')
# tts.save("audio/voice.mp3")
# ---------------------------------------------




# ------------Пути
voice_path = "audio/voice.mp3"
text_path = "text_file/text.txt"
fx_dir = Path("audio/fx")
output_path = "result.wav"

# Шаг 1. Распознаём текст (или берём из файла)
with open(text_path, "r", encoding="utf-8") as f:
    text = f.read()

# Шаг 2. Анализируем текст на события
doc = nlp(text)

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

for sent in doc.sents:
    for token in sent:
        for key, fx in keywords.items():
            if key in token.lemma_:
                events.append({"text": sent.text, "sound": fx})
                break

# Шаг 3. Расчёт позиций (равномерно распределяем)
voice = AudioSegment.from_mp3(voice_path)
duration = len(voice)
positions = list(range(1000, duration - 1000, max(1000, duration // len(events))))

# Шаг 4. Загружаем звуки и микшируем
fx_track = AudioSegment.silent(duration=duration)

for event, pos in zip(events, positions):
    fx_path = fx_dir / event["sound"]
    fx = AudioSegment.from_wav(fx_path).fade_in(500).fade_out(1000) - 10
    fx_track = fx_track.overlay(fx, position=pos)

# Шаг 5. Финальный микс
final = voice.overlay(fx_track)
final.export(output_path, format="wav")
print(f"✅ Готово: {output_path}")
print(f"✅ Готово: {events}")