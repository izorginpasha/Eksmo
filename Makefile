# Makefile

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# Установить виртуальное окружение и зависимости
setup:
	python -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Сгенерировать события из голосового файла (Whisper + Ollama)
generate:
	$(PYTHON) generate_events.py

# Применить эффекты и создать финальный звук
apply:
	$(PYTHON) apply_events.py

# Полный процесс: генерация + применение
run: generate apply

# Удалить временные файлы
clean:
	rm -f events.xlsx result.wav

# Удалить окружение
nuke:
	rm -rf $(VENV)
