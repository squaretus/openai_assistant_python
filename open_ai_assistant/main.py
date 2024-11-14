# import os
import psycopg2
import pandas as pd
# from langchain import hub
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from langchain_ollama.chat_models import ChatOllama

from uuid import uuid4

from langchain_chroma import Chroma

from langchain_community.document_loaders import PyPDFLoader

data_dir = "/app/open_ai_assistant/learning_base"

# Подключение к PostgreSQL
db_conn = psycopg2.connect(
    dbname='api_prod',
    user='karo_user',
    password='1',
    host='db',
    port='5432'
)

# Запрос для получения фильмов и сеансов на текущий день
def fetch_today_sessions():
    query = """SELECT s.started_at::text AS \"Дата и время начала сеанса\",
                      f.title AS \"Название фильма\",
                      f.actors AS \"Актеры в фильме\",
                      c.name AS \"Название кинотеатра\",
                      ct.name AS \"Название города кинотеатра\"
               FROM sessions AS s
               LEFT JOIN films AS f ON s.film_id = f.id
               LEFT JOIN cinemas AS c ON s.cinema_id = c.id
               LEFT JOIN cities AS ct ON s.city_id = ct.id
               WHERE s.started_at >= CURRENT_TIMESTAMP
               ORDER BY s.started_at ASC
               LIMIT 10"""

    # Загружаем результат запроса в DataFrame
    df = pd.read_sql(query, db_conn)

    df = df.fillna("Пусто")

    # Преобразуем DataFrame в список словарей
    return df.to_dict(orient='records')

sessions = fetch_today_sessions()

# files = []

# prompt = hub.pull("rlm/rag-prompt")

instructions = (
    "Ты виртуальный киноэксперт. Ты должен отвечать на вопросы пользователей "
    "только исходя из контекста, представленного в запросе. Не используй информацию "
    " из сторонних источников и отвечай на вопросы, связанные только с сеансами, "
    "просмотром кино, вопросы о фильмах и актерах."
)

prompt = PromptTemplate.from_template(
    "instructions: {instructions}\n\ncontext: {context}\n\nquestion: {question}"
)

llm = ChatOllama(
    base_url='http://192.168.1.80:11434',
    model='qwen2.5:14b'
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# for file in os.listdir(data_dir):
#     loader = PyPDFLoader(f"""{data_dir}/{file}""")
#     for f in loader.load():
#         files.append(f)

# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=300,
#     chunk_overlap=30
# )

# documents = text_splitter.split_documents(files)

embeddings = OllamaEmbeddings(
    base_url='http://192.168.1.80:11434',
    model="nomic-embed-text"
)

vectorstore = Chroma(
    collection_name="ollama",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

documents = [
    Document(
        page_content=f"{session}",
        metadata=session
    )
    for session in sessions
]

uuids = [str(uuid4()) for _ in range(len(sessions))]

vectorstore.add_documents(documents=documents, ids=uuids)

query = 'Какие 3 фильма можно посмотреть сегодня?'

qa_chain = (
    {
        "instructions": RunnableLambda(lambda _: instructions),
        "context": vectorstore.as_retriever() | format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)

response = qa_chain.invoke(query)

print(response)
