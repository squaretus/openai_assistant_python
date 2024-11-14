import os
from time import sleep
import numpy
from openai import OpenAI
import PyPDF2
import chromadb

from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

ollama_embedding_function = OllamaEmbeddingFunction(
    url='http://192.168.1.80:11434/api/embeddings',
    model_name='qwen2.5:14b'
)

client = OpenAI(
    base_url='http://192.168.1.80:11434/v1/',
    api_key='ollama',
)

data_dir = "/app/open_ai_assistant/learning_base"
texts = []
file_names = []

# Функция для извлечения текста из PDF
def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        number_of_pages = len(reader.pages)
        for page_number in range(number_of_pages):
            page = reader.pages[page_number]
            text = page.extract_text()
            return text.strip()

# Считываем текст из PDF файлов
for file_name in os.listdir(data_dir):
    if file_name.endswith('.pdf'):
        file_path = os.path.join(data_dir, file_name)
        try:
            text = extract_text_from_pdf(file_path)
            texts.append(text.replace("\n", ""))
            file_names.append(file_name)
        except Exception as e:
            print(f"Ошибка при обработке файла {file_name}: {e}")

# Создаем эмбеддинги для текстов с помощью OpenAI
def get_embedding(text):
    response = ollama_embedding_function(text)
    return response

# Создаем Chroma DB клиент и коллекцию
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name='ollama')

# Добавляем документы и эмбеддинги в коллекцию
for i, text in enumerate(texts):
    embeddings = client.embeddings.create(model='nomic-embed-text', input=text).data[0].embedding

    collection.add(
        documents=[text],
        metadatas=[{"file_name": file_names[i]}],
        embeddings=embeddings,
        ids=[file_names[i]]
    )

collection

# # Поиск по запросу
# def search(query, top_k=5):
#     query_embedding = get_embedding(query)
#     results = collection.query(
#         query_embeddings=[query_embedding],
#         n_results=top_k
#     )
#     search_results = [
#         (res['metadata']['file_name'], res['document'], res['distance'])
#         for res in results['results'][0]
#     ]
#     return search_results

# query = "Соленый попкорн"
# results = search(query)

# print(results)

# chat_completion = client.chat.completions.create(
#     messages=[
#         {
#             'role': 'user',
#             'content': 'А ты в курсе, что сегодня вообще-то 8 ноября 2024 года 15:03',
#         }
#     ],
#     model='qwen2.5:14b',
# )

# print(chat_completion.choices[0].message.content)
