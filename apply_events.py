from pydub import AudioSegment
from pydub.generators import Sine, WhiteNoise
from pathlib import Path
import pandas as pd
import hashlib
import webbrowser

def apply_pan(audio: AudioSegment, pan_value: float) -> AudioSegment:
    try:
        return audio.pan(pan_value)
    except Exception as e:
        print(f"⚠️ Ошибка применения панорамы ({pan_value}): {e}")
        return audio

def mix_effects(audio_path, fx_dir, events_path="events.xlsx", output_path="result.wav"):
    try:
        voice = AudioSegment.from_file(audio_path)
    except Exception as e:
        print(f"❌ Ошибка загрузки голосового файла: {e}")
        return

    try:
        df = pd.read_excel(events_path)
    except Exception as e:
        print(f"❌ Ошибка чтения {events_path}: {e}")
        return

    if df.empty:
        print("⚠️ Таблица событий пуста.")
        return

    required_columns = {"sound", "start_ms", "duration_ms", "volume_db"}
    for col in required_columns:
        if col not in df.columns:
            print(f"❌ Нет обязательного столбца: {col}")
            return

    max_end_ms = (df["start_ms"] + df["duration_ms"]).max()
    total_duration = max(len(voice), max_end_ms)
    print(f"🕒 Длительность микса: {total_duration / 1000:.2f} сек")

    if total_duration > len(voice):
        voice += AudioSegment.silent(duration=total_duration - len(voice))

    fx_track = AudioSegment.silent(duration=total_duration)
    applied = 0

    for index, row in df.iterrows():
        def load_sound(name_column: str):
            filename = str(row[name_column]).strip()
            if not filename.endswith(".wav"):
                filename += ".wav"
            fx_path = fx_dir / filename

            if fx_path.exists():
                return AudioSegment.from_wav(fx_path)

            # Если файл не найден — ищем вручную в BBC
            base_name = filename.replace("_", " ").replace(".wav", "")
            bbc_url = f"https://sound-effects.bbcrewind.co.uk/search?q={base_name}"
            print(f"❗ [{index}] Файл '{filename}' не найден. Поиск в BBC: {bbc_url}")
            try:
                webbrowser.open(bbc_url)
            except:
                pass
            return None

        # Загрузка основного эффекта
        fx = load_sound("sound")
        if fx is None:
            continue

        # Обработка параметров
        fx_duration = int(row["duration_ms"])
        if len(fx) > fx_duration:
            fx = fx[:fx_duration]

        # Громкость
        fx += float(row.get("volume_db", 0))

        # Панорама
        pan = float(row.get("pan", 0.0))
        fx = apply_pan(fx, pan)

        # Фейды
        fx = fx.fade_in(300).fade_out(500)

        # Вставка
        start_ms = int(row["start_ms"])
        fx_track = fx_track.overlay(fx, position=start_ms)
        print(f"✅ [{index}] {row['sound']} → {start_ms} мс | {fx_duration} мс | vol: {row['volume_db']} | pan: {pan}")
        applied += 1

        # Фоновый шум
        bg_name = row.get("background_noise", "")
        if pd.notna(bg_name) and str(bg_name).strip():
            bg = load_sound("background_noise")
            if bg:
                bg = bg - 10  # делаем фоновый звук тише
                fx_track = fx_track.overlay(bg, position=start_ms)
                print(f"🎧 Добавлен фон: {bg_name}")

    if applied == 0:
        print("⚠️ Ни один эффект не был применён.")
        return

    try:
        final = voice.overlay(fx_track)
        final.export(output_path, format="wav")
        print(f"🎧 Финальный файл сохранён: {output_path}")
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")

def main():
    audio_path = "audio/voice.mp3"
    fx_dir = Path("audio/fx")
    fx_dir.mkdir(parents=True, exist_ok=True)
    mix_effects(audio_path, fx_dir)

if __name__ == "__main__":
    main()
