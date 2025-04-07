import numpy as np
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from sentence_transformers import SentenceTransformer
import logging

# Загрузка настроек из config.json
with open("config.json", "r") as f:
    config = json.load(f)

# Чтение активной модели и списка моделей
active_model_index = config.get("active_model_index", 0)
models_list = config.get("models", [])
if not models_list:
    raise Exception("Не задан ни один путь к модели в конфигурации.")

MODEL_NAME = models_list[active_model_index]["name"]

# Настройка логирования (файл и консоль)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Обработчик для файла
file_handler = logging.FileHandler("server.log")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler.setFormatter(file_formatter)

# Обработчик для консоли
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info("Запуск сервера с моделью %s", MODEL_NAME)

# Загрузка модели
try:
    model = SentenceTransformer(MODEL_NAME)
except Exception as e:
    logger.error("Ошибка загрузки модели %s: %s", MODEL_NAME, e)
    raise e

def normalize_vector(v):
    v = v / np.linalg.norm(v)
    return v.tolist()

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

            # Векторизация
            embedding = model.encode([input_text], convert_to_numpy=True)
            embedding = normalize_vector(embedding[0])

            self._set_headers()
            self.wfile.write(json.dumps({"vector": embedding}).encode('utf-8'))

        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")

def run(port=config["server"]["port"]):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHandler)
    logger.info("Сервер запущен на порту %d", port)
    httpd.serve_forever()

if __name__ == '__main__':
    run()
