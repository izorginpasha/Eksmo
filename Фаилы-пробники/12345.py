import requests
import json
import pandas as pd
from pathlib import Path
import re

# Чтение текста из файла
with open("../text_file/text.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

# Удаление переносов строк внутри предложений, если нужно
text = re.sub(r"(?<![.\n])\n(?![\n])", " ", raw_text.strip())

# Промпт с инструкцией в формате JSON
prompt = f"""
Ты — звуковой дизайнер.

Проанализируй художественный абзац и разбей его на логические звуковые сцены. Верни результат строго в JSON-формате, как список объектов. Каждый объект должен включать:

- "scene": название сцены (2–4 слова)
- "text": фрагмент оригинального текста
- "sounds": список звуков, каждый из которых содержит:
   - "file": имя файла в формате `название.wav`
   - "description": краткое описание (например, «топот по доскам»)
   - "volume": от -20 до 0
   - "pan": от -1.0 до 1.0

Вот текст для анализа:

\"\"\"{text}\"\"\"
"""

# Отправка запроса к Ollama
response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "mistral:latest", "prompt": prompt, "stream": False}
)

# Ответ модели
data = response.json()
print(data["response"])  # Для отладки

# Парсинг и сохранение результата в Excel
def save_json_scenes_to_excel(json_text, output_file="output/scene_list.xlsx"):
    try:
        scenes = json.loads(json_text)
    except json.JSONDecodeError as e:
        print("❌ Ошибка JSON:", e)
        return

    rows = []
    for scene in scenes:
        for sound in scene["sounds"]:
            rows.append({
                "scene": scene["scene"],
                "text": scene["text"],
                "sound_file": sound["file"],
                "description": sound["description"],
                "volume": sound["volume"],
                "pan": sound["pan"]
            })

    df = pd.DataFrame(rows)
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False)
    print(f"✅ Сцены и звуки сохранены в: {output_path}")
    return output_path

# Сохраняем
save_json_scenes_to_excel(data["response"])
