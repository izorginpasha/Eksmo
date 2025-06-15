import requests
import json
import pandas as pd
from pathlib import Path

# Обновлённый промпт
prompt = """
Ты — звуковой дизайнер.

Проанализируй художественный абзац и разбей его на логические звуковые сцены. Верни результат строго в JSON-формате, как список объектов. Каждый объект — это одна звуковая сцена и должен включать:

- "scene": название сцены (2–4 слова)
- "text": фрагмент оригинального текста
- "sounds": список звуков, каждый из которых содержит:
   - "file": имя файла в формате `название.wav`
   - "description": краткое описание (например, «топот по доскам»)
   - "volume": от -20 до 0
   - "pan": от -1.0 до 1.0

Пример структуры одного объекта:
{
  "scene": "Шум и волнение",
  "text": "…строка из абзаца…",
  "sounds": [
    {
      "file": "waves.wav",
      "description": "всплески волн",
      "volume": -6,
      "pan": -0.5
    },
    ...
  ]
}

Вот текст для анализа:

"Джо не открывал глаза, а только слушал, что происходит вокруг. А вокруг был шум, который нарастал с каждой секундой. Шум этот состоял из многих звуков: громкие разговоры людей, всплески морских волн, скрежет железных механизмов, крики чаек, топот ног, свист ветра, скрип досок и многих-многих других. Звук от шагов человека, который их нёс, тоже изменился. Сначала они были почти не слышные, чуть-чуть шаркающие, видимо, он шёл по земле, а теперь мало того, что стали очень громкие, так ещё и каждый шаг сопровождался неприятным железным эхом. Ящик поставили, и шаги начали отдаляться, пока совсем не стихли. Больше к ним никто не подходил, и, судя по звукам, рядом ничего не происходило. Джо, подождав ещё несколько минут, решил открыть глаза."
"""

# Запрос к модели
response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "mistral:latest", "prompt": prompt, "stream": False}
)

data = response.json()
print(data["response"])  # Для отладки

# Парсинг ответа модели и сохранение в Excel
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

# Сохраняем результат
save_json_scenes_to_excel(data["response"])
