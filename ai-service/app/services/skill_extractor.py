"""Deterministic skill extraction and alias normalization service with evidence preservation."""

import re
from typing import Dict, List, Optional, Set, Tuple
from app.schemas.extraction import SkillEvidence
from app.services.skill_ontology import CANONICAL_SKILLS, SkillDefinition


def extract_evidence_snippet(text: str, start_char: int, end_char: int, window_words: int = 25) -> str:
    """Extract a surrounding window of text around a matched character span (EC-33).

    Guarantees:
        - Extracts up to `window_words` before and after the match.
        - Joins with ellipsis ('...') if trimmed.
        - Verbatim snippet preservation without modification.
    """
    pre_text = text[:start_char].strip()
    post_text = text[end_char:].strip()
    matched = text[start_char:end_char]

    pre_words = pre_text.split() if pre_text else []
    post_words = post_text.split() if post_text else []

    left_slice = pre_words[-window_words:] if len(pre_words) > window_words else pre_words
    right_slice = post_words[:window_words] if len(post_words) > window_words else post_words

    left_str = " ".join(left_slice)
    right_str = " ".join(right_slice)

    prefix = "... " if len(pre_words) > window_words else ""
    suffix = " ..." if len(post_words) > window_words else ""

    parts = []
    if left_str:
        parts.append(f"{prefix}{left_str}")
    parts.append(matched)
    if right_str:
        parts.append(f"{right_str}{suffix}")

    return " ".join(parts).strip()


class SkillExtractor:
    """Deterministic extractor matching canonical skills and aliases against normalized text."""

    def __init__(self, ontology: Optional[List[SkillDefinition]] = None):
        self.ontology = ontology or CANONICAL_SKILLS
        self._compiled_matchers: List[Tuple[SkillDefinition, List[re.Pattern]]] = []
        self._compile_ontology()

    def _compile_ontology(self) -> None:
        """Compile regex patterns with boundary assertions and negative lookahead guards."""
        for skill in self.ontology:
            patterns: List[re.Pattern] = []

            if skill.custom_regex:
                flags = 0 if skill.case_sensitive else re.IGNORECASE
                patterns.append(re.compile(skill.custom_regex, flags))
            else:
                for alias in skill.aliases:
                    escaped = re.escape(alias)
                    flags = 0 if skill.case_sensitive else re.IGNORECASE

                    # Special handling for trailing punctuation in symbols like C++, C#, .NET
                    if alias.endswith(("+", "#")):
                        boundary_pattern = rf"\b{escaped}"
                    elif alias.startswith((".", "/")):
                        boundary_pattern = rf"{escaped}\b"
                    else:
                        boundary_pattern = rf"\b{escaped}\b"

                    if skill.negative_lookahead:
                        boundary_pattern = f"{boundary_pattern}{skill.negative_lookahead}"

                    patterns.append(re.compile(boundary_pattern, flags))

            self._compiled_matchers.append((skill, patterns))

    def extract_skills(self, normalized_text: str) -> Tuple[List[SkillEvidence], List[SkillEvidence]]:
        """Extract skills and technical tools with evidence from normalized resume text.

        Returns:
            Tuple of (primary_skills, technical_tools)
        """
        if not normalized_text or not normalized_text.strip():
            return [], []

        primary_skills: List[SkillEvidence] = []
        technical_tools: List[SkillEvidence] = []
        seen_canonical: Set[str] = set()

        for skill_def, patterns in self._compiled_matchers:
            if skill_def.canonical_name in seen_canonical:
                continue

            best_match: Optional[re.Match] = None
            for pattern in patterns:
                match = pattern.search(normalized_text)
                if match:
                    best_match = match
                    break

            if best_match:
                seen_canonical.add(skill_def.canonical_name)
                matched_str = best_match.group(0).strip()
                start_char, end_char = best_match.span()
                snippet = extract_evidence_snippet(normalized_text, start_char, end_char)

                evidence = SkillEvidence(
                    canonical_name=skill_def.canonical_name,
                    matched_text=matched_str,
                    category=skill_def.category,
                    evidence_snippet=snippet,
                    confidence=1.0,
                )

                if skill_def.is_technical_tool:
                    technical_tools.append(evidence)
                else:
                    primary_skills.append(evidence)

        # Sort alphabetically by canonical name for deterministic output
        primary_skills.sort(key=lambda s: s.canonical_name)
        technical_tools.sort(key=lambda s: s.canonical_name)

        return primary_skills, technical_tools


# Module singleton
_extractor_instance: Optional[SkillExtractor] = None


def get_skill_extractor() -> SkillExtractor:
    """Return singleton instance of SkillExtractor."""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = SkillExtractor()
    return _extractor_instance
