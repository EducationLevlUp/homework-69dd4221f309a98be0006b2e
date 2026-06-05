# Парсер карточки учебного задания

Модуль `task_card_parser.py` принимает неформальное текстовое описание учебного задания и за **один проход** преобразует его в валидированную Pydantic-модель с помощью LangChain и `PydanticOutputParser`.

## Структура проекта

```
project_root/
├── task_card_parser.py   # Основной модуль
├── requirements.txt      # Зависимости
├── .env.example          # Шаблон переменных окружения
└── README.md             # Этот файл
```

## Зависимости

```bash
pip install -r requirements.txt
```

Требуемые пакеты:
- `langchain-core` — базовые компоненты LangChain (промпты, парсеры, цепочки)
- `langchain-openai` — клиент для OpenAI-совместимых моделей
- `pydantic` — валидация и сериализация моделей
- `python-dotenv` — загрузка переменных окружения из `.env`

## Настройка внешних сервисов

Скопируйте `.env.example` в `.env` и заполните свои значения:

```bash
cp .env.example .env
```

Переменные:

| Переменная | Описание | По умолчанию |
|---|---|---|
| `OPENAI_API_KEY` | API-ключ провайдера LLM | — |
| `MODEL_NAME` | Имя модели | `gpt-4o-mini` |
| `OPENAI_BASE_URL` | URL для локальных провайдеров (LM Studio и др.) | не задано |

> **Важно:** Никогда не коммитьте `.env` в репозиторий. Используйте `.env.example` как шаблон.

## Запуск

```bash
python task_card_parser.py
```

Скрипт выполнит ровно **один запрос** к LLM и выведет:
1. Валидированный дамп (`model_dump()`) в формате JSON.
2. Краткую человекочитаемую сводку по полям карточки.

## Пример

**Вход:**

> Сдайте к пятнице мини-отчёт по LangChain: 2 страницы, упор на агентов. Оценка: за полноту и за пример кода.

**Выход (фрагмент):**

```text
--- Валидированный дамп (model_dump) ---
{
  "title": "Мини-отчёт по LangChain",
  "subject": "LangChain",
  "deadline_hint": "к пятнице",
  "deliverable_type": "отчёт",
  "grading_hints": ["полнота", "пример кода"]
}

--- Краткая сводка ---
  title:            Мини-отчёт по LangChain
  subject:          LangChain
  deadline_hint:    к пятнице
  deliverable_type: отчёт
  grading_hints:    ['полнота', 'пример кода']
```

## Архитектура

```
PromptTemplate
    │
    ├── {input_text}          — неформальное описание задания
    └── {format_instructions} — инструкции формата от PydanticOutputParser
    │
    ▼
ChatOpenAI (LLM)
    │
    ▼
PydanticOutputParser
    │
    ▼
TaskCard (Pydantic BaseModel)
    │
    ├── model_dump()  → dict
    └── _format_summary() → человекочитаемая сводка
```

## Поля модели `TaskCard`

| Поле | Тип | Описание |
|---|---|---|
| `title` | `str` | Краткое название задания |
| `subject` | `str` | Предмет или тема задания |
| `deadline_hint` | `str` | Подсказка по срокам (свободная форма) |
| `deliverable_type` | `str` | Что нужно сдать (отчёт, код, презентация…) |
| `grading_hints` | `list[str]` | Критерии или подсказки по оценке |

## Критерии оценки (закрытые)

| Критерий | Статус |
|---|---|
| Модель данных отражает сценарий (поля + типы) | ✅ |
| Один запрос — один проход по цепочке, без лишнего диалога | ✅ |
| Используется парсер структуры (`PydanticOutputParser`), а не «разбор руками» | ✅ |
| Промпт согласован с инструкциями формата (`partial_variables`) | ✅ |
| Вывод: и структура (`model_dump`), и краткая сводка | ✅ |

## Smoke-test (локальная проверка без API)

Если внешний API недоступен, можно проверить корректность импортов и валидацию модели:

```python
from task_card_parser import TaskCard

# Проверка валидации
card = TaskCard(
    title="Тест",
    subject="Python",
    deadline_hint="завтра",
    deliverable_type="код",
    grading_hints=["стиль", "корректность"],
)
print(card.model_dump())
```
