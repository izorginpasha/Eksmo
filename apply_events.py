from pydub import AudioSegment
from pydub.generators import Sine, WhiteNoise
from pathlib import Path
import pandas as pd
import hashlib

def generate_synthetic_sound(fx_path: Path):
    """Создаёт уникальный звук на основе имени файла."""
    name = fx_path.stem.lower()
    hash_val = int(hashlib.md5(name.encode()).hexdigest(), 16)

    # Псевдо-уникальные параметры
    freq = 200 + (hash_val % 800)        # частота: 200–1000 Гц
    dur = 5000 + (hash_val % 1000)        # длительность: 300–1300 мс
    is_noise = "noise" in name or "wind" in name or "static" in name

    if is_noise:
        sound = WhiteNoise().to_audio_segment(duration=dur).fade_in(100).fade_out(100)
    else:
        sound = Sine(freq).to_audio_segment(duration=dur).fade_in(100).fade_out(100)

    try:
        sound.export(fx_path, format="wav")
        print(f"🔧 Авто-сгенерирован звук: {fx_path.name} ({freq} Гц, {dur} мс)")
        return fx_path
    except Exception as e:
        print(f"❌ Ошибка генерации {fx_path.name}: {e}")
        return None


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

    max_end_ms = (df["start_ms"] + df["duration_ms"]).max()
    total_duration = max(len(voice), max_end_ms)
    print(f"🕒 Длительность микса: {total_duration / 1000:.2f} сек")

    if total_duration > len(voice):
        voice += AudioSegment.silent(duration=total_duration - len(voice))

    fx_track = AudioSegment.silent(duration=total_duration)
    applied = 0

    for index, row in df.iterrows():
        fx_path = fx_dir / str(row["sound"])

        if not fx_path.exists():
            print(f"⚠️ [{index}] Файл не найден: {fx_path}")
            # fx_path = generate_synthetic_sound(fx_path)
            if not fx_path or not fx_path.exists():
                continue  # пропускаем, если не удалось сгенерировать

        try:
            fx = AudioSegment.from_wav(fx_path)
            fx_duration = int(row["duration_ms"])
            if len(fx) > fx_duration:
                fx = fx[:fx_duration]

            fx += float(row["volume_db"])
            fx = fx.fade_in(300).fade_out(500)

            start_ms = int(row["start_ms"])
            fx_track = fx_track.overlay(fx, position=start_ms)
            print(f"✅ [{index}] {fx_path.name} → {start_ms} мс | {len(fx)} мс | dB")
            applied += 1

        except Exception as e:
            print(f"❌ [{index}] Ошибка обработки {fx_path.name}: {e}")

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
