import json
import requests
import re
from pathlib import Path
from utilities.utilities import save_events_to_excel,save_events_to_json

def compress_sfx_by_scene(
    input_path="output/events.json",
    output_path="output/compressed_sfx.json",
    model_name="mistral:latest"
):
    # Загружаем сегменты из файла
    with open(input_path, "r", encoding="utf-8") as f:
        segments = json.load(f)

    print(f"📥 Загружено сегментов: {len(segments)}")
    print("📦 Подготовка данных для модели...")

    # Преобразуем список сегментов в формат для анализа (JSON текст)
    description = json.dumps(segments, ensure_ascii=False, indent=2)

    # Prompt для модели
    prompt = f"""
Ты — звуковой дизайнер.

Ниже список звуковых сегментов с текстом, временем и эффектами.

Проанализируй их как одну звуковую сцену и верни только те эффекты, которые действительно стоит использовать. 
Можешь объединять, менять время или удалять лишнее.

Верни список в формате JSON.
Формат ответа строго такой:

[
  {{
    "sound": "описание звука",
    "start": 12.0,
    "end": 25.3,
    "volume": -5,
    "pan": 0.0,
    "text": "текст при котором производится звук"
  }}
]

Никаких пояснений. Только JSON. Вот данные:

{description}
"""

    try:
        print("🚀 Отправка запроса в модель...")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": False}
        )
        result = response.json().get("response", "").strip()
        print("📤 Ответ от модели получен")

        match = re.search(r'\[(?:.|\n)*?\]', result)
        final_sfx = eval(match.group(0)) if match else []
        print(f"✅ Найдено эффектов: {len(final_sfx)}")
        print("🔍 Preview:\n", json.dumps(final_sfx[:2], indent=2, ensure_ascii=False))  # Покажи первые 2
    except Exception as e:
        print("❌ Ошибка при запросе к модели:", e)
        final_sfx = []

    # Сохраняем результат в файл
    out_path = Path(output_path)
    # Сохраняем JSON-файл
    save_events_to_json(final_sfx, output_path)
    # Сохраняем  в ексель

    save_events_to_excel(final_sfx, output_path="output/compressed_events.xlsx")
    return out_path
