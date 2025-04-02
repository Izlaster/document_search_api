import json
import os
import numpy as np
import faiss
from http.server import BaseHTTPRequestHandler, HTTPServer
from sentence_transformers import SentenceTransformer
from transformers import AutoModel

# Конфигурация (укажите свои пути и модель)
MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
FAISS_INDEX_PATH = 'results_BERT_Default/text_index.faiss'
FILENAMES_PATH = 'results_BERT_Default/filenames.npy'
VECTORS_PATH = 'results_BERT_Default/vectors'
TEXT_FILES_DIR = 'texts'  # Директория с текстовыми файлами (если требуется)
TOP_K = 20  # Количество возвращаемых похожих текстов

# Загрузка модели, FAISS индекса и списка имён файлов
model = SentenceTransformer(MODEL_NAME)
index = faiss.read_index(FAISS_INDEX_PATH)
filenames = np.load(FILENAMES_PATH, allow_pickle=True)

def split_text_by_length(text, max_length=1000):
    words = text.split()
    chunks = []
    current_chunk = ""
    for word in words:
        if len(current_chunk) + len(word) + 1 <= max_length:
            current_chunk = current_chunk + " " + word if current_chunk else word
        else:
            chunks.append(current_chunk)
            current_chunk = word
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def get_document_embedding(text, model, chunk_size=1000):
    if len(text) <= chunk_size:
        return model.encode(text)
    else:
        chunks = split_text_by_length(text, max_length=chunk_size)
        chunk_embeddings = model.encode(chunks, convert_to_numpy=True)
        return np.mean(chunk_embeddings, axis=0)

def process_file_content(file_content, top_k=TOP_K):
    """
    Принимает содержимое текстового файла, вычисляет его вектор с помощью модели,
    сохраняет вектор в файл и выполняет поиск похожих текстов через FAISS.
    Возвращает вектор запроса и список найденных похожих файлов с их схожестью.
    """
    query_text = file_content.strip()
    
    # Вычисление векторного представления запроса
    query_embedding = model.encode([query_text], convert_to_numpy=True)
    query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
    
    # Сохранение вектора запроса (опционально)
    os.makedirs(VECTORS_PATH, exist_ok=True)
    vector_file_path = os.path.join(VECTORS_PATH, "query_vector.txt")
    np.savetxt(vector_file_path, query_embedding, delimiter=",", fmt="%.6f")
    
    # Поиск похожих текстов с использованием FAISS
    distances, indices = index.search(query_embedding.astype('float32'), top_k)
    
    similar_texts = []
    for i, idx in enumerate(indices[0]):
        text_filename = filenames[idx]
        # Расчёт схожести в процентах
        similarity = max(0, (1 - distances[0][i] / 2)) * 100
        similar_texts.append({
            "filename": text_filename,
            "similarity": round(similarity, 2)
        })
    return query_embedding.tolist(), similar_texts

class SimpleHandler(BaseHTTPRequestHandler):
    def _set_headers(self, response_code=200):
        self.send_response(response_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
    def do_GET(self):
        self._set_headers()
        response = {"message": "Hello, this is the vectorization API."}
        self.wfile.write(json.dumps(response).encode('utf-8'))
        
    def do_POST(self):
        # Обработка только для эндпоинта /api/vector
        if self.path != "/api/vector":
            self.send_error(404, "Endpoint not found")
            return
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        try:
            # Ожидаем, что в теле запроса передан текстовый файл в формате plain text
            file_content = post_data.decode('utf-8')
        except UnicodeDecodeError:
            self.send_error(400, "Invalid text encoding")
            return
        
        try:
            query_vector, similar_texts = process_file_content(file_content)
            response = {
                "query_vector": query_vector,
                "similar_texts": similar_texts
            }
            self._set_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")

def run(server_class=HTTPServer, handler_class=SimpleHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Сервер запущен на порту {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
