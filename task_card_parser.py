"""
task_card_parser.py — модуль разбора неформального описания учебного задания
в валидированную Pydantic-модель (карточку задания) за один проход.

Использует LangChain: PromptTemplate → LLM → PydanticOutputParser.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# 1. Загрузка переменных окружения
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# 2. Pydantic-модель карточки задания
# ---------------------------------------------------------------------------

class TaskCard(BaseModel):
    """Структурированная карточка учебного задания."""

    title: str = Field(description="Краткое название задания")
    subject: str = Field(description="Предмет или тема задания")
    deadline_hint: str = Field(description="Подсказка по срокам (свободная форма)")
    deliverable_type: str = Field(
        description="Что нужно сдать: отчёт, код, презентация и т. п."
    )
    grading_hints: list[str] = Field(
        default_factory=list,
        description="Список критериев или подсказок по оценке",
    )


# ---------------------------------------------------------------------------
# 3. Парсер и промпт
# ---------------------------------------------------------------------------

_parser = PydanticOutputParser(pydantic_object=TaskCard)

_prompt = PromptTemplate(
    template=(
        "Ты — ассистент, который разбирает описание учебного задания.\n"
        "Извлеки из текста следующие поля и верни их строго в формате,\n"
        "указанном ниже.\n\n"
        "{format_instructions}\n\n"
        "Текст задания:\n{input_text}"
    ),
    input_variables=["input_text"],
    partial_variables={
        "format_instructions": _parser.get_format_instructions()
    },
)


# ---------------------------------------------------------------------------
# 4. Инициализация LLM
# ---------------------------------------------------------------------------

_llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
    temperature=0.0,
    base_url=os.getenv("OPENAI_BASE_URL", None),
)


# ---------------------------------------------------------------------------
# 5. Цепочка (chain)
# ---------------------------------------------------------------------------

_chain = _prompt | _llm | _parser


# ---------------------------------------------------------------------------
# 6. Форматирование краткой сводки
# ---------------------------------------------------------------------------

def _format_summary(card: TaskCard) -> str:
    """Возвращает человекочитаемую краткую сводку по карточке."""
    lines: list[str] = [
        f"  title:            {card.title}",
        f"  subject:          {card.subject}",
        f"  deadline_hint:    {card.deadline_hint}",
        f"  deliverable_type: {card.deliverable_type}",
        f"  grading_hints:    {card.grading_hints}",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 7. Основная функция — один проход
# ---------------------------------------------------------------------------

def parse_task(raw_text: str) -> TaskCard:
    """
    Преобразует неформальное описание задания в валидированную карточку.

    Выполняет ровно один запрос к LLM через цепочку
    PromptTemplate → LLM → PydanticOutputParser.

    Возвращает экземпляр TaskCard.
    """
    result: TaskCard = _chain.invoke({"input_text": raw_text})
    return result


# ---------------------------------------------------------------------------
# 8. Демонстрация / точка входа
# ---------------------------------------------------------------------------

def _demo(raw_text: str) -> None:
    """Запускает разбор и выводит результат в консоль."""
    print("=" * 60)
    print("Входной текст:")
    print(f"  {raw_text}")
    print("=" * 60)

    try:
        card = parse_task(raw_text)
    except Exception as exc:
        print(f"Ошибка при разборе: {exc}", file=sys.stderr)
        sys.exit(1)

    # --- Валидированный дамп (dict) ---
    print("\n--- Валидированный дамп (model_dump) ---")
    dump: dict[str, Any] = card.model_dump()
    print(json.dumps(dump, ensure_ascii=False, indent=2))

    # --- Краткая человекочитаемая сводка ---
    print("\n--- Краткая сводка ---")
    print(_format_summary(card))
    print("=" * 60)


if __name__ == "__main__":
    # Пример входа из условия задания
    sample_task = (
        "Сдайте к пятнице мини-отчёт по LangChain: 2 страницы, упор на агентов. "
        "Оценка: за полноту и за пример кода."
    )
    _demo(sample_task)
