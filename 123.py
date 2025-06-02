import requests
import json
import re
import pandas as pd
from pathlib import Path
prompt = """
Ты — звуковой дизайнер.

Проанализируй художественный абзац и разбей его на логические звуковые сцены. Для каждой сцены укажи:

1. 🎬 Название сцены (2–4 слова)
2. 📖 Текст сцены (скопируй нужные строки из абзаца)
3. 🔊 Какие звуковые эффекты соответствуют этому моменту
   - имя файла звука в формате `название.wav`
   - громкость (`volume`: от -20 до 0)
   - панорама (`pan`: от -1.0 до 1.0)
4. ⏱ Время (start – end) в секундах — предположительно

Формат вывода:

🎬 Название сцены  
Текст:  
"...сюжет сцены..."

🔊 Звуки:  
- sound_1.wav (volume: -6, pan: -0.5)  
- sound_2.wav (volume: -3, pan: 0.3)



📜 Вот текст для анализа:

"Джо не открывал глаза, а только слушал, что происходит вокруг. А вокруг был шум, который нарастал с каждой секундой. Шум этот состоял из многих звуков: громкие разговоры людей, всплески морских волн, скрежет железных механизмов, крики чаек, топот ног, свист ветра, скрип досок и многих-многих других. Звук от шагов человека, который их нёс, тоже изменился. Сначала они были почти не слышные, чуть-чуть шаркающие, видимо, он шёл по земле, а теперь мало того, что стали очень громкие, так ещё и каждый шаг сопровождался неприятным железным эхом. Ящик поставили, и шаги начали отдаляться, пока совсем не стихли. Больше к ним никто не подходил, и, судя по звукам, рядом ничего не происходило. Джо, подождав ещё несколько минут, решил открыть глаза."
"""

response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "mistral:latest", "prompt": prompt, "stream": False}
)

data = response.json()
print(data["response"])

def parse_scene_response_to_excel(text: str, output_file: str = "output/scene_from_prompt.xlsx"):
    """
    Парсит структурированный ответ модели в стиле:
    🎬 Сцена
    Текст: ...
    🔊 Звуки: ...
    Время: X.0 – Y.0 сек

    И сохраняет это в Excel-таблицу
    """
    scenes = []
    current_scene = None
    current_text = ""
    start_time, end_time = None, None

    lines = text.strip().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("🎬"):
            current_scene = line.replace("🎬", "").strip()
            current_text = ""
            start_time, end_time = None, None
            i += 1

        elif line.startswith("Текст:"):
            current_text = line.replace("Текст:", "").strip()
            i += 1

        elif line.startswith("🔊") or line.startswith("- "):
            i += 1
            while i < len(lines) and lines[i].strip().startswith("- "):
                s_line = lines[i].strip()
                match = re.search(r'([\w\-]+\.wav).*?volume:\s*(-?\d+).*?pan:\s*(-?\d*\.?\d+)', s_line)
                if match:
                    sound = match.group(1)
                    volume = int(match.group(2))
                    pan = float(match.group(3))
                    scenes.append({
                        "scene": current_scene,
                        "sound": sound,
                        "start": start_time,
                        "end": end_time,
                        "volume": volume,
                        "pan": pan,
                        "text": current_text
                    })
                i += 1

        elif line.lower().startswith("время"):
            time_match = re.search(r'([\d\.]+)\s*[-–]\s*([\d\.]+)', line)
            if time_match:
                start_time = float(time_match.group(1))
                end_time = float(time_match.group(2))
                for s in reversed(scenes):
                    if s["start"] is None:
                        s["start"] = start_time
                        s["end"] = end_time
                    else:
                        break
            i += 1
        else:
            i += 1

    df = pd.DataFrame(scenes)
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False)
    print(f"✅ Таблица сцен сохранена: {output_path}")
    return output_path

parse_scene_response_to_excel(data["response"])