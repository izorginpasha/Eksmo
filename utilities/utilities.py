import pandas as pd
import json
from pathlib import Path

def save_events_to_excel(events, output_path="output/events.xlsx"):
    if not events:
        print("⚠️ Нет событий для сохранения.")
        return

    df = pd.DataFrame(events)

    # Вычисляем длительность и технические поля
    df["start_sec"] = df["start"]
    df["end_sec"] = df["end"]
    df["duration_sec"] = df["end"] - df["start"]

    df["start_ms"] = (df["start_sec"] * 1000).astype(int)
    df["duration_ms"] = (df["duration_sec"] * 1000).astype(int)
    df["volume_db"] = df["volume"]

    # Упорядочиваем столбцы для читаемости
    df = df[[
        "text", "sound", "start_sec", "duration_sec", "end_sec", "volume_db","pan",
        "start_ms", "duration_ms"
    ]]

    df.to_excel(output_path, index=False)
    print(f"✅ События сохранены в {output_path}")


def mitation_acting():
    #-------------Имитация озвучки диктора - -------
    # Путь к тексту
    with open("text_file/text.txt", "r", encoding="utf-8") as f:
        text = f.read()

    # Озвучка текста через gTTS
    tts = gTTS(text, lang='ru')
    tts.save("audio/voice.mp3")

def save_events_to_json(events, output_path="output/events.json"):
    # Сохраняем JSON-файл для дальнейшего анализа/дообучения
    json_path = Path(output_path)
    json_path.parent.mkdir(exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    print(f"📄 События сохранены в JSON: {json_path}")