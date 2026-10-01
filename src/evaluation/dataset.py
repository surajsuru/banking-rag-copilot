import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List
from src.logger import get_logger

logger = get_logger(__name__)

@dataclass
class EvalQuestion:
    id: str
    question: str
    expected_sources: List[str]
    answer_type: str
    category: str = "unknown"
    min_relevant_chunks: int = 1
    required_role: str = "operations"
    guard_expectation: str = ""


def load_dataset(path: str = "data/evaluation/evaluation_questions.json") -> List[EvalQuestion]:
    """
    Loads evaluation questions from the JSON benchmark file.
    """
    filepath = Path(path)
    
    if not filepath.exists():
        raise FileNotFoundError(f"Evaluation dataset not found at: {filepath}")
    
    with open(filepath, "r", encoding="utf-8") as f:
        raw = json.load(f)
    
    questions = []
    for item in raw["questions"]:
        questions.append(EvalQuestion(
            id=item["id"],
            question=item["question"],
            expected_sources=item.get("expected_sources", []),
            answer_type=item.get("answer_type", "unknown"),
            category=item.get("category", "unknown"),
            min_relevant_chunks=item.get("min_relevant_chunks", 1),
            required_role=item.get("required_role", "operations"),
            guard_expectation=item.get("guard_expectation", "")
        ))
    
    logger.info(f"Loaded {len(questions)} evaluation questions from '{filepath}'")
    return questions
