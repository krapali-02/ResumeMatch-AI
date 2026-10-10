"""Extraction request and response schemas."""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


class SkillEvidence(BaseModel):
    """Structured skill representation preserving grounded verbatim evidence."""

    canonical_name: str = Field(description="Canonical, normalized skill identifier")
    matched_text: str = Field(description="Exact verbatim alias or string located in resume")
    category: str = Field(description="Technical taxonomy category (e.g., language, database, devops)")
    evidence_snippet: str = Field(description="Surrounding textual context window demonstrating usage")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence score")


class EducationEntry(BaseModel):
    """Structured candidate educational credential."""

    degree: Optional[str] = Field(default=None, description="Degree or credential (e.g., Bachelor of Science)")
    field_of_study: Optional[str] = Field(default=None, description="Major or field (e.g., Computer Science)")
    institution: Optional[str] = Field(default=None, description="Educational institution / university name")
    graduation_year: Optional[int] = Field(default=None, description="Explicit graduation or enrollment year")
    evidence_snippet: Optional[str] = Field(default=None, description="Verbatim quote snippet supporting the entry")


class ExperienceSummary(BaseModel):
    """Explicitly stated career tenure distinguishing unknown from confirmed absence (EC-08)."""

    explicit_years_of_experience: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Explicitly identified total years of professional experience",
    )
    status: Literal["identified", "unknown", "confirmed_absent"] = Field(
        default="unknown",
        description="Knowledge state of candidate tenure",
    )
    evidence_snippet: Optional[str] = Field(
        default=None,
        description="Verbatim snippet where experience length was explicitly stated or derived",
    )


class RoleEntry(BaseModel):
    """Structured representation of a professional work experience entry."""

    title: Optional[str] = Field(default=None, description="Job or role title")
    company: Optional[str] = Field(default=None, description="Employing company or organization")
    duration: Optional[str] = Field(default=None, description="Reported date range or duration")
    description: str = Field(default="", description="Role summary or responsibilities")
    evidence_snippet: str = Field(default="", description="Verbatim text snippet from resume")


class ExtractRequest(BaseModel):
    """Request payload for resume text extraction."""

    text: str = Field(
        ...,
        description="Normalized raw resume text stream",
    )
    candidate_id: Optional[str] = Field(
        default=None,
        description="Optional upstream candidate identifier for correlation",
    )
    options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional extraction flags or tuners",
    )

    @field_validator("text")
    @classmethod
    def validate_text_not_empty(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Resume text cannot be empty or solely whitespace.")
        return trimmed


class ExtractResponse(BaseModel):
    """Structured extraction response contract."""

    candidate_id: Optional[str] = Field(default=None, description="Echoed candidate identifier")
    skills: List[SkillEvidence] = Field(default_factory=list, description="Primary technical skills with evidence")
    technical_tools: List[SkillEvidence] = Field(
        default_factory=list,
        description="Supporting platforms, infrastructure tools, and methodologies",
    )
    education: List[EducationEntry] = Field(default_factory=list, description="Educational history entries")
    education_status: Literal["identified", "unknown", "confirmed_absent"] = Field(
        default="unknown",
        description="Status distinguishing unknown education from confirmed absence (EC-08)",
    )
    experience_summary: ExperienceSummary = Field(
        default_factory=ExperienceSummary,
        description="Identified or unknown experience tenure summary",
    )
    roles: List[RoleEntry] = Field(default_factory=list, description="Identified work experiences and roles")
    roles_status: Literal["identified", "unknown", "confirmed_absent"] = Field(
        default="unknown",
        description="Status distinguishing unknown roles from confirmed absence",
    )
    character_count: int = Field(description="Character count of analyzed text")
    extraction_notes: List[str] = Field(
        default_factory=list,
        description="Informational diagnostics or low-confidence indicators (EC-04)",
    )
    contains_prompt_injection_attempt: bool = Field(
        default=False,
        description="Whether adversarial instruction patterns were detected in the untrusted text (EC-15)",
    )
