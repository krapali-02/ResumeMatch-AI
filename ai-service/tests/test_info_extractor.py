"""Unit tests for education, tenure, and role extraction."""

from app.services.info_extractor import (
    extract_education,
    extract_experience_summary,
    extract_roles,
)


def test_education_extraction_standard(sample_resume_text):
    """Verify standard degree, field of study, institution, and year extraction."""
    entries, status = extract_education(sample_resume_text)

    assert status == "identified"
    assert len(entries) >= 1

    entry = entries[0]
    assert entry.degree == "Bachelor of Science"
    assert entry.field_of_study == "Computer Science"
    assert "Berkeley" in (entry.institution or "")
    assert entry.graduation_year == 2018
    assert entry.evidence_snippet is not None


def test_education_unknown_when_not_mentioned():
    """Verify resumes omitting education are categorized as 'unknown' rather than failed (EC-08)."""
    text = "John Doe\nSelf-employed consultant specializing in Docker and Kubernetes orchestration."
    entries, status = extract_education(text)

    assert status == "unknown"
    assert len(entries) == 0


def test_education_confirmed_absent():
    """Verify explicit statement of no degree is categorized as 'confirmed_absent' (EC-08)."""
    text = "Alex Smith\nSelf-taught developer with no college education and no formal degree."
    entries, status = extract_education(text)

    assert status == "confirmed_absent"
    assert len(entries) == 0


def test_explicit_experience_tenure_identified():
    """Verify explicit years of experience phrases are extracted reliably."""
    cases = [
        ("Full-stack engineer with 6+ years of professional experience.", 6.0),
        ("Over 8 years of experience building distributed systems.", 8.0),
        ("Senior Developer with 4.5 years of industry experience.", 4.5),
        ("Experience: 10+ years in software engineering.", 10.0),
    ]

    for text, expected_years in cases:
        summary = extract_experience_summary(text)
        assert summary.status == "identified"
        assert summary.explicit_years_of_experience == expected_years
        assert summary.evidence_snippet is not None


def test_experience_unknown_when_not_mentioned():
    """Verify absence of tenure statements yields 'unknown' state without fabrication (EC-08)."""
    text = "Candidate profile with skills in Python and SQL."
    summary = extract_experience_summary(text)

    assert summary.status == "unknown"
    assert summary.explicit_years_of_experience is None
    assert summary.evidence_snippet is None


def test_experience_confirmed_absent():
    """Verify fresh graduates or candidates with 0 experience are confirmed absent."""
    text = "Recent college graduate. Entry-level with no experience looking for junior roles."
    summary = extract_experience_summary(text)

    assert summary.status == "confirmed_absent"
    assert summary.explicit_years_of_experience == 0.0


def test_role_extraction(sample_resume_text):
    """Verify chronological roles, companies, and date ranges are parsed."""
    roles, status = extract_roles(sample_resume_text)

    assert status == "identified"
    assert len(roles) >= 2

    senior_role = next((r for r in roles if "Senior" in (r.title or "")), None)
    assert senior_role is not None
    assert "Acme" in (senior_role.company or "")
    assert "Present" in (senior_role.duration or "")
    assert len(senior_role.description) > 0


def test_roles_unknown_when_not_mentioned():
    """Verify text without job listings returns unknown status."""
    text = "Summary of technical skills: Python, React, Docker."
    roles, status = extract_roles(text)

    assert status == "unknown"
    assert len(roles) == 0
