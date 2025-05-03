from pydub import AudioSegment
from pathlib import Path
import pandas as pd

def mix_effects(audio_path, fx_dir, events_path="events.xlsx"):
    voice = AudioSegment.from_mp3(audio_path)
    duration = len(voice)
    fx_track = AudioSegment.silent(duration=duration)

    df = pd.read_excel(events_path)
    for _, row in df.iterrows():
        fx_path = fx_dir / row["sound"]
        if fx_path.exists():
            fx = AudioSegment.from_wav(fx_path).fade_in(300).fade_out(500) - 10
            fx_track = fx_track.overlay(fx, position=int(row["position"]))
        else:
            print(f"⚠️ Не найден звук: {fx_path}")

    final = voice.overlay(fx_track)
    final.export("result.wav", format="wav")
    print("✅ Финальный файл сохранён: result.wav")

def main():
    audio_path = "audio/voice.mp3"
    fx_dir = Path("audio/fx")
    mix_effects(audio_path, fx_dir)

if __name__ == "__main__":
    main()
