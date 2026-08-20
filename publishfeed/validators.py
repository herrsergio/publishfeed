"""Validation functions for LLM-generated content.

These are used with Mellea's simple_validate() to check generated text
without additional LLM calls. Each function returns (passed: bool, reason: str).
"""

import re
from typing import Tuple, List


FIRST_PERSON_PATTERNS = [
    r'\bI\b',
    r'\bwe\b',
    r'\bmy\b',
    r'\bour\b',
    r'\bmine\b',
    r'\bus\b',
    r'\bme\b',
    r'\bmyself\b',
    r'\bourselves\b',
    r'\bjoin us\b',
    r'\bwe created\b',
    r'\bwe are\b',
    r"\bwe're\b",
    r"\bwe've\b",
    r"\bwe'll\b",
    r'\bour team\b',
    r'\bour new\b',
    r'\blet us\b',
    r"\blet's\b",
    r'\bwe believe\b',
    r'\bwe think\b',
    r'\bwe built\b',
    r'\bwe launched\b',
    r'\bwe released\b',
    r'\bwe developed\b',
    r'\bwe introduced\b',
    r'\bwe announce\b',
]

_FIRST_PERSON_REGEX = re.compile(
    '|'.join(FIRST_PERSON_PATTERNS),
    re.IGNORECASE
)


def no_first_person_pronouns(text: str) -> Tuple[bool, str]:
    """Check that text contains no first-person pronouns or related phrases.

    Args:
        text: The generated text to validate

    Returns:
        A tuple of (passed: bool, reason: str).
        If passed is False, reason explains what was found (fed back to model on retry).
    """
    match = _FIRST_PERSON_REGEX.search(text)
    if match:
        found = match.group()
        return (
            False,
            f"Found first-person language: '{found}'. "
            "Rewrite using third-person perspective only."
        )
    return (True, "No first-person pronouns found.")


def get_all_first_person_matches(text: str) -> List[str]:
    """Return all first-person matches in the text (for debugging/logging)."""
    return _FIRST_PERSON_REGEX.findall(text)
