from transformers import AutoTokenizer, AutoModelForCausalLM

model_id = "Qwen/Qwen2-1.5B-Instruct"
save_path = "../qwen_model"

print("Загрузка модели...")
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
tokenizer.save_pretrained(save_path)

model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
model.save_pretrained(save_path)

print("✅ Модель успешно сохранена в", save_path)
