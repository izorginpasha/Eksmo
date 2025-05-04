import pandas as pd  # В начало, если ещё не добавлено

def save_events_to_excel(events, output_path="events.xlsx"):
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
        "text", "sound",
        "start_sec", "duration_sec", "end_sec",
        "start_ms", "duration_ms", "volume_db"
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