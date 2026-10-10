"""Candidate information extraction API endpoint."""

import logging
from fastapi import APIRouter, HTTPException, status
from app.config import get_settings
from app.schemas.extraction import ExtractRequest, ExtractResponse
from app.services.info_extractor import (
    extract_education,
    extract_experience_summary,
    extract_roles,
)
from app.services.skill_extractor import get_skill_extractor
from app.services.text_normalizer import normalize_resume_text

logger = logging.getLogger("resumematch.ai.extract")
router = APIRouter(prefix="/api/v1", tags=["Candidate Extraction"])


@router.post(
    "/extract",
    response_model=ExtractResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract Structured Candidate Information",
    description="Converts normalized resume text into structured skills, tools, education, tenure, and work experience.",
)
def extract_candidate_info(payload: ExtractRequest) -> ExtractResponse:
    settings = get_settings()

    # 1. Guard against excessive length (EC-09 / DoS mitigation)
    if len(payload.text) > settings.MAX_INPUT_TEXT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Input text exceeds maximum allowed length of {settings.MAX_INPUT_TEXT_LENGTH} characters.",
        )

    # 2. Text normalization and untrusted instruction isolation (EC-15)
    normalized_text, contains_injection = normalize_resume_text(payload.text)

    # Scanned document or empty text check (EC-01, EC-04)
    if len(normalized_text) < 50:
        notes = ["Low extractable character yield. Possible scanned or unreadable document."]
    else:
        notes = []

    if contains_injection:
        notes.append("Adversarial instruction pattern detected and neutralized. Text parsed as passive data.")
        logger.warning(
            "Adversarial instruction detected in extraction request for candidate: %s",
            payload.candidate_id or "anonymous",
        )

    # 3. Deterministic skill and technical tool extraction with evidence
    skill_extractor = get_skill_extractor()
    primary_skills, technical_tools = skill_extractor.extract_skills(normalized_text)

    # 4. Education extraction distinguishing unknown from confirmed absence (EC-08)
    education_entries, edu_status = extract_education(normalized_text)

    # 5. Experience tenure summary (explicitly stated or derived)
    experience_summary = extract_experience_summary(normalized_text)

    # 6. Roles and work experiences
    roles, roles_status = extract_roles(normalized_text)

    return ExtractResponse(
        candidate_id=payload.candidate_id,
        skills=primary_skills,
        technical_tools=technical_tools,
        education=education_entries,
        education_status=edu_status,
        experience_summary=experience_summary,
        roles=roles,
        roles_status=roles_status,
        character_count=len(normalized_text),
        extraction_notes=notes,
        contains_prompt_injection_attempt=contains_injection,
    )
