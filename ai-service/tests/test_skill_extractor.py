"""Unit tests for deterministic skill extraction, alias canonicalization, and evidence preservation."""

from app.services.skill_extractor import SkillExtractor, extract_evidence_snippet


def test_alias_normalization_canonical_mapping():
    """Verify common skill aliases resolve to canonical entities without inventing skills."""
    extractor = SkillExtractor()
    text = "Candidate has expertise in JS, TS, Postgres, K8s, Golang, and ReactJS."
    primary, tools = extractor.extract_skills(text)

    all_canonical = {s.canonical_name for s in primary + tools}

    assert "JavaScript" in all_canonical
    assert "TypeScript" in all_canonical
    assert "PostgreSQL" in all_canonical
    assert "Kubernetes" in all_canonical
    assert "Go" in all_canonical
    assert "React" in all_canonical

    # Check that aliases mapped correctly
    js_match = next(s for s in primary if s.canonical_name == "JavaScript")
    assert js_match.matched_text.lower() == "js"

    postgres_match = next(s for s in primary if s.canonical_name == "PostgreSQL")
    assert postgres_match.matched_text.lower() == "postgres"

    k8s_match = next(s for s in tools if s.canonical_name == "Kubernetes")
    assert k8s_match.matched_text.lower() == "k8s"


def test_atomic_boundary_polysemous_guards():
    """Verify 'JavaScript' does not extract false positive 'Java' (EC-22)."""
    extractor = SkillExtractor()
    text = "Proficient in JavaScript development and building modern React web apps."
    primary, _ = extractor.extract_skills(text)

    canonical_names = [s.canonical_name for s in primary]
    assert "JavaScript" in canonical_names
    assert "Java" not in canonical_names, "False positive 'Java' extracted from 'JavaScript'!"


def test_go_language_vs_english_verb():
    """Verify 'Go' is only extracted in programming context, not from conversational verb 'go'."""
    extractor = SkillExtractor()
    # Conversational use
    text_verb = "I plan to go to the conference and learn new skills."
    primary_verb, _ = extractor.extract_skills(text_verb)
    assert "Go" not in [s.canonical_name for s in primary_verb]

    # Explicit programming context
    text_prog = "Skills: Golang, Python, Docker"
    primary_prog, _ = extractor.extract_skills(text_prog)
    assert "Go" in [s.canonical_name for s in primary_prog]


def test_special_characters_cpp_csharp():
    """Verify languages with symbols like C++ and C# extract cleanly."""
    extractor = SkillExtractor()
    text = "Developed embedded systems in C++ and backend enterprise services in C#."
    primary, _ = extractor.extract_skills(text)

    names = {s.canonical_name for s in primary}
    assert "C++" in names
    assert "C#" in names


def test_evidence_snippet_preservation():
    """Verify matched skills retain verbatim evidence snippets (EC-33)."""
    extractor = SkillExtractor()
    text = "Led architecture of distributed microservices utilizing FastAPI and PostgreSQL database."
    primary, tools = extractor.extract_skills(text)

    fastapi_skill = next(s for s in primary if s.canonical_name == "FastAPI")
    assert "FastAPI" in fastapi_skill.evidence_snippet
    assert "microservices" in fastapi_skill.evidence_snippet

    postgres_skill = next(s for s in primary if s.canonical_name == "PostgreSQL")
    assert "PostgreSQL" in postgres_skill.evidence_snippet


def test_snippet_windowing_boundary():
    """Verify evidence snippet windowing logic trims excessive words with ellipsis."""
    words = [f"word{i}" for i in range(100)]
    text = " ".join(words[:50]) + " TARGET " + " ".join(words[50:])
    start = text.index("TARGET")
    end = start + len("TARGET")

    snippet = extract_evidence_snippet(text, start, end, window_words=10)
    assert snippet.startswith("...")
    assert snippet.endswith("...")
    assert "TARGET" in snippet


def test_deduplication_of_repeated_skills():
    """Verify skills repeated multiple times in text appear only once (EC-35)."""
    extractor = SkillExtractor()
    text = "Python is great. I love Python. Used Python at company A and Python at company B."
    primary, _ = extractor.extract_skills(text)

    python_skills = [s for s in primary if s.canonical_name == "Python"]
    assert len(python_skills) == 1
