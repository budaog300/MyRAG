# RAG Framework

Это модульный фреймворк для Retrieval-Augmented Generation (RAG), построенный с прицелом на расширяемость и переиспользование в разных проектах.

Поддерживает несколько стратегий поиска (vector, keyword, hybrid) и построен по принципам чистой архитектуры.

---

## 🚀 Возможности

- 🔎 Векторный поиск (На данный Qdrant)
- 🔑 Ключевой поиск (На данный Elasticsearch)
- 🔀 Гибридный поиск (RRF)
- 🧠 Чанкинг документов
- ⚡ Асинхронная архитектура
- 🧩 Плагинная система (retrievers, rerankers, компрессоры)

---

## 🧱 Архитектура

```plaintext
    src/
    │
    ├── api/               API слой (HTTP интерфейс)
    │   ├── routes/
    │   ├── schemas/
    │   ├── deps.py        Зависимости
    │
    ├── rag/               RAG ядро
    │   ├── services/      Оркестрация пайплайна
    │   ├── retrieval/     Vector / BM25 / Hybrid
    │   ├── repository/    Адаптеры хранилищ (Qdrant, Elastic и т.д.)
    │   ├── components/    Сборка RAG пайплайна
    │   ├── llm/           LLM слой
    │   ├── schemas/       Доменные модели (RAGDocument и др.)
    │   ├── utils/         Вспомогательные утилиты
    │
    ├── core/              Конфиги, логирование, утилиты
    └── main.py            Точка входа в сервис
```

---

## ⚙️ Конфигурация окружения (Пример)

.env.qdrant
QDRANT_URL=<http://localhost:6333>
QDRANT_API_KEY=api-key

.env.elastic
ELASTIC_URL=<http://localhost:9200>
ELASTIC_API_KEY=api-key

.env.ai (Можно использовать любой агрегатор)
API_URL=<https://api.vsegpt.ru/v1/chat/completions>
BASE_URL=<https://api.vsegpt.ru/v1>
API_KEY=api-key

---

## ▶️ Запуск сервиса

```bash
docker compose up -d --build
```

---

## 📥 Индексация документов в файле src/scripts/upload_docs.py

```bash
python -m src.scripts.upload_docs
```

---

## 🔍 Типы поиска

1) 🔎 Векторный поиск
Семантический поиск через эмбеддинги.

2) 🔑 Ключевой поиск
BM25-поиск.

3) 🔀 Гибридный поиск
Комбинация нескольких источников через RRF.

---

## 🔌 Расширяемость

Можно легко добавить:

- новые vector DB (Milvus, Weaviate)
- новые keyword движки
- компрессоры / summarization / рефразеры
- кастомные пайплайны

---

## 🧪 Пример пайплайна

Запрос → Retriever (Vector + BM25)
       → Fusion (RRF)
       → Reranker (опционально)
       → Ответ

---

## 📈 Дальнейшее развитие

- Config-driven pipeline builder
- Evaluation (recall@k, latency)
- CLI интерфейс
- очередь ingestion

---

## 🧑‍💻 Автор

Фреймворк для построения и экспериментов с RAG-системами с возможностью масштабирования под продакшн
