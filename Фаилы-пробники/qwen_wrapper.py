from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_PATH = "../qwen_model"

# Кэшируем модель и токенайзер при первом импорте
_tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
_model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, trust_remote_code=True).eval().to("cuda" if torch.cuda.is_available() else "cpu")


def ask(prompt: str, max_tokens: int = 200) -> str:
    """
    Получить ответ от Qwen2-1.5B-Instruct
    """
    inputs = _tokenizer(prompt, return_tensors="pt").to(_model.device)
    outputs = _model.generate(**inputs, max_new_tokens=max_tokens)
    return _tokenizer.decode(outputs[0], skip_special_tokens=True)
