import os
import numpy as np
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from sentence_transformers import SentenceTransformer
import logging

# === Базовая директория проекта ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# === Пути ===
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
MODELS_DIR = os.path.join(BASE_DIR, "models")
DEFAULT_LOG_PATH = os.path.join(BASE_DIR, "server.log")
SYSTEM_LOG_PATH = "/var/log/document_search/log.log"

# === Загрузка настроек ===
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

active_model_index = config.get("active_model_index", 0)
models_list = config.get("models", [])
if not models_list:
    raise Exception("Не задан ни один путь к модели в конфигурации.")

# Имя модели и локальный путь
MODEL_HF_NAME = models_list[active_model_index]["name"]
MODEL_LOCAL_NAME = MODEL_HF_NAME.replace("/", "_")
LOCAL_MODEL_PATH = os.path.join(MODELS_DIR, MODEL_LOCAL_NAME)

# Убедимся, что директория models существует
os.makedirs(MODELS_DIR, exist_ok=True)

# === Настройка логирования ===
log_path = SYSTEM_LOG_PATH if os.access(os.path.dirname(SYSTEM_LOG_PATH), os.W_OK) else DEFAULT_LOG_PATH

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(log_path)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info("Запуск сервера с моделью %s", MODEL_HF_NAME)

# === Загрузка модели ===
try:
    if os.path.exists(LOCAL_MODEL_PATH):
        logger.info("Локальная модель найдена по пути %s. Загружаю в оффлайн-режиме.", LOCAL_MODEL_PATH)
        model = SentenceTransformer(LOCAL_MODEL_PATH)
    else:
        logger.info("Модель не найдена локально. Пытаюсь скачать %s и сохранить в %s...", MODEL_HF_NAME, MODELS_DIR)
        model = SentenceTransformer(MODEL_HF_NAME, cache_folder=MODELS_DIR)
        logger.info("Модель %s успешно скачана и сохранена.", MODEL_HF_NAME)
except Exception as e:
    logger.error("Ошибка загрузки модели %s: %s", MODEL_HF_NAME, e)
    raise e

# === Вспомогательная функция ===
def normalize_vector(v):
    v = v / np.linalg.norm(v)
    return v.tolist()

# === Обработчик HTTP-запросов ===
class SimpleHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def do_POST(self):
        if self.path != "/api/vector":
            self.send_error(404, "Not Found")
            return

        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data.decode('utf-8'))
            input_text = data.get("text", "").strip()

            if not input_text:
                self.send_error(400, "Missing 'text' in JSON body")
                return

            embedding = model.encode([input_text], convert_to_numpy=True)
            embedding = normalize_vector(embedding[0])

            self._set_headers()
            self.wfile.write(json.dumps({"vector": embedding}).encode('utf-8'))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")

# === Запуск сервера ===
def run(port=config["server"]["port"]):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHandler)
    logger.info("Сервер запущен на порту %d", port)
    httpd.serve_forever()

if __name__ == '__main__':
    run()
