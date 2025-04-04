import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from sentence_transformers import SentenceTransformer
import numpy as np

# Загружаем модель один раз
MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
model = SentenceTransformer(MODEL_NAME)

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

def run(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHandler)
    print(f"Сервер запущен на порту {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
