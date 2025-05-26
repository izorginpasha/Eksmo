from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoModelForTokenClassification
from sentence_transformers import SentenceTransformer
from pathlib import Path
from pprint import pprint
import os

text = """
— Ты ведь не уйдёшь? — спросила Анна, всматриваясь в вечернее небо. Ветер завывал в соснах, а где-то вдалеке лаяла собака. Пётр подошёл ближе и обнял её. 
— Никогда.
"""

# === Пути к локальным моделям ===
models_dir = Path("./models")
sentiment_path = models_dir / "rubert-sentiment"
ner_path = models_dir / "ru-ner-bert"
embed_path = models_dir / "all-minilm"

# === Предзагрузка моделей при необходимости ===
def download_and_cache():
    models_dir.mkdir(exist_ok=True)

    # 1. Sentiment
    if not sentiment_path.exists():
        tokenizer = AutoTokenizer.from_pretrained("blanchefort/rubert-base-cased-sentiment")
        model = AutoModelForSequenceClassification.from_pretrained("blanchefort/rubert-base-cased-sentiment")
        tokenizer.save_pretrained(sentiment_path)
        model.save_pretrained(sentiment_path)

    # 2. NER
    if not ner_path.exists():
        tokenizer = AutoTokenizer.from_pretrained("ai-forever/ru-ner-bert")
        model = AutoModelForTokenClassification.from_pretrained("ai-forever/ru-ner-bert")

    # 3. Sentence embeddings
    if not embed_path.exists():
        model = SentenceTransformer("all-MiniLM-L6-v2")
        model.save(embed_path)

# === Загрузка моделей из кэша ===
def load_models():
    sentiment_pipe = pipeline("sentiment-analysis", model=sentiment_path)
    ner_pipe = pipeline("ner", model=ner_path, aggregation_strategy="simple")
    embed_model = SentenceTransformer(embed_path)
    return sentiment_pipe, ner_pipe, embed_model

# === Главный анализ ===
def main():
    download_and_cache()
    sentiment_pipe, ner_pipe, embed_model = load_models()

    sentiment_result = sentiment_pipe(text)
    ner_result = ner_pipe(text)
    embeddings = embed_model.encode([text])

    print("\n[Сентимент анализа]")
    pprint(sentiment_result)

    print("\n[Именованные сущности]")
    pprint(ner_result)

    print("\n[Эмбеддинг формы]")
    print(embeddings[0][:10])

if __name__ == "__main__":
    main()
