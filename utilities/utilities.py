import pandas as pd  # В начало, если ещё не добавлено

def save_events_to_excel(events, output_path="events.xlsx"):
    if not events:
        print("⚠️ Нет событий для сохранения.")
        return
    df = pd.DataFrame(events)
    df["time_sec"] = df["position"] / 1000
    df = df[["text", "sound", "position", "time_sec"]]
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