"""Text normalization, unicode standardization, and untrusted data sanitization."""

import re
import unicodedata
from typing import Tuple

# Common prompt injection signatures embedded in adversarial resumes (EC-15)
PROMPT_INJECTION_PATTERNS = [
    r"(?i)\bignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions\b",
    r"(?i)\bdisregard\s+(?:all\s+)?(?:previous|prior|above)\s+instructions\b",
    r"(?i)\[\s*system\s*(?:prompt|notice|directive|instruction|override)\b",
    r"(?i)\b(?:system|admin|root)\s*:\s*override\b",
    r"(?i)\baward\s+(?:this\s+)?candidate\s+(?:a\s+)?(?:score|rating)\s+of\s+100%",
    r"(?i)\brank\s+(?:as\s+)?#?1\s+(?:applicant|candidate)\b",
    r"(?i)\bset\s+match\s+score\s+to\s+100\b",
    r"(?i)\byou\s+are\s+now\s+in\s+developer\s+mode\b",
    r"(?i)\bdo\s+not\s+evaluate\s+this\s+resume\b",
]

_COMPILED_INJECTION_PATTERNS = [re.compile(p) for p in PROMPT_INJECTION_PATTERNS]


def normalize_resume_text(raw_text: str) -> Tuple[str, bool]:
    """Normalize extracted resume text into clean, standardized representation.

    Returns:
        Tuple of (normalized_text, contains_prompt_injection_attempt)

    Guarantees:
        - NFKC Unicode normalization (fixes ligatures 'fi'/'fl', decomposes accents).
        - Standardizes typographical quotes, dashes, and whitespace.
        - Strips harmful control characters while preserving structural layout.
        - Isolates untrusted adversarial instructions (EC-15).
    """
    if not raw_text:
        return "", False

    # 1. Unicode NFKC normalization
    text = unicodedata.normalize("NFKC", raw_text)

    # 2. Check for adversarial instruction injections (passive detection)
    contains_injection = False
    for pattern in _COMPILED_INJECTION_PATTERNS:
        if pattern.search(text):
            contains_injection = True
            break

    # 3. Replace non-standard whitespace and typographical quotes/dashes
    text = text.replace("\u00a0", " ")  # Non-breaking space
    text = text.replace("\u200b", "")   # Zero-width space
    text = text.replace("\ufeff", "")   # Byte order mark

    # Replace typographical quotes with standard ASCII equivalents
    text = re.sub(r"[\u2018\u2019\u201a\u201b]", "'", text)
    text = re.sub(r"[\u201c\u201d\u201e\u201f]", '"', text)

    # Replace typographical dashes with standard hyphen
    text = re.sub(r"[\u2010\u2011\u2012\u2013\u2014\u2015]", "-", text)

    # 4. Remove unprintable control characters, preserving \n and \t
    cleaned_chars = []
    for ch in text:
        if ch in ("\n", "\t", "\r") or (unicodedata.category(ch)[0] != "C" and ord(ch) >= 32):
            cleaned_chars.append(ch)
    text = "".join(cleaned_chars)

    # 5. Standardize newlines: CRLF -> LF, CR -> LF
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 6. Normalize horizontal whitespace (spaces and tabs)
    text = re.sub(r"[ \t]+", " ", text)

    # 7. Collapse excessive consecutive line breaks (3 or more -> 2)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 8. Clean trailing line whitespace
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines).strip()

    return text, contains_injection
