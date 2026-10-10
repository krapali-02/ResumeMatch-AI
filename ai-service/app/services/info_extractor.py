"""Information extraction service for education, experience tenure, and roles."""

import re
from typing import List, Optional, Tuple
from app.schemas.extraction import (
    EducationEntry,
    ExperienceSummary,
    RoleEntry,
)
from app.services.skill_extractor import extract_evidence_snippet

# Degree classifications
DEGREE_PATTERNS = [
    (
        "Doctor of Philosophy",
        re.compile(r"\b(?:Ph\.?D\.?|Doctor of Philosophy|Doctorate)\b", re.IGNORECASE),
    ),
    (
        "Master of Science",
        re.compile(r"\b(?:M\.?S\.?|Master of Science|M\.?Sc\.?|M\.?Tech\.?|M\.?E\.?)\b", re.IGNORECASE),
    ),
    (
        "Master of Business Administration",
        re.compile(r"\b(?:M\.?B\.?A\.?|Master of Business Administration)\b", re.IGNORECASE),
    ),
    (
        "Master of Computer Applications",
        re.compile(r"\b(?:M\.?C\.?A\.?|Master of Computer Applications)\b", re.IGNORECASE),
    ),
    (
        "Bachelor of Science",
        re.compile(r"\b(?:B\.?S\.?|Bachelor of Science|B\.?Sc\.?)\b", re.IGNORECASE),
    ),
    (
        "Bachelor of Technology",
        re.compile(r"\b(?:B\.?Tech\.?|Bachelor of Technology|B\.?E\.?|Bachelor of Engineering)\b", re.IGNORECASE),
    ),
    (
        "Bachelor of Computer Applications",
        re.compile(r"\b(?:B\.?C\.?A\.?|Bachelor of Computer Applications)\b", re.IGNORECASE),
    ),
    (
        "Bachelor of Arts",
        re.compile(r"\b(?:B\.?A\.?|Bachelor of Arts)\b", re.IGNORECASE),
    ),
    (
        "Associate Degree",
        re.compile(r"\b(?:A\.?S\.?|Associate of Science|Associate Degree)\b", re.IGNORECASE),
    ),
    (
        "High School Diploma",
        re.compile(r"\b(?:High School Diploma|Secondary School Certificate|HSC)\b", re.IGNORECASE),
    ),
]

FIELDS_OF_STUDY = [
    "Computer Science",
    "Information Technology",
    "Software Engineering",
    "Computer Engineering",
    "Data Science",
    "Artificial Intelligence",
    "Electrical Engineering",
    "Electronics and Communication",
    "Mechanical Engineering",
    "Information Systems",
    "Mathematics",
    "Statistics",
    "Physics",
    "Business Administration",
    "Cybersecurity",
]

UNIVERSITY_KEYWORDS = re.compile(
    r"\b(?:University|College|Institute of Technology|Polytechnic|Academy|School of (?:Engineering|Computing))\b",
    re.IGNORECASE,
)

# Explicit years of experience patterns
EXPLICIT_EXP_PATTERNS = [
    re.compile(
        r"(\d+(?:\.\d+)?)\+?\s*(?:to\s*\d+\s*)?(?:years?|yrs?)(?:\s+of)?\s+(?:professional|relevant|industry|work|hands-on|engineering|software)?\s*experience",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:over|more than|approximately)\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)(?:\s+of)?\s+experience",
        re.IGNORECASE,
    ),
    re.compile(
        r"experience\s*:\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
        re.IGNORECASE,
    ),
]

# Patterns indicating confirmed absence of qualifications / experience
CONFIRMED_ABSENCE_EXP = re.compile(
    r"\b(?:no prior (?:work )?experience|0 years (?:of )?experience|entry[- ]level with no experience|fresh graduate)\b",
    re.IGNORECASE,
)
CONFIRMED_ABSENCE_EDU = re.compile(
    r"\b(?:no formal degree|self[- ]taught developer with no college|no degree)\b",
    re.IGNORECASE,
)

# Common professional job titles
COMMON_JOB_TITLES = [
    r"Senior Software Engineer",
    r"Software Engineer",
    r"Principal Engineer",
    r"Staff Software Engineer",
    r"Lead Software Engineer",
    r"Full[- ]Stack Developer",
    r"Full[- ]Stack Engineer",
    r"Backend Developer",
    r"Backend Engineer",
    r"Frontend Developer",
    r"Frontend Engineer",
    r"DevOps Engineer",
    r"Site Reliability Engineer",
    r"Cloud Architect",
    r"Data Scientist",
    r"Machine Learning Engineer",
    r"AI Engineer",
    r"System Administrator",
    r"QA Engineer",
    r"Quality Assurance Engineer",
    r"Technical Lead",
    r"Engineering Manager",
    r"Product Manager",
    r"Software Developer",
    r"Web Developer",
    r"Database Administrator",
    r"Security Engineer",
]

_JOB_TITLES_PATTERN = re.compile(
    r"\b(?:" + "|".join(COMMON_JOB_TITLES) + r")\b",
    re.IGNORECASE,
)

# Date range pattern for experience roles (e.g., "Jan 2021 - Present", "2018 - 2021", "06/2019 - 08/2022")
_DATE_RANGE_PATTERN = re.compile(
    r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+)?\b(20\d{2}|19\d{2})\b\s*[-–—to]+\s*(?:(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+)?\b(20\d{2}|19\d{2})\b|Present|Current|Now)",
    re.IGNORECASE,
)


def extract_education(text: str) -> Tuple[List[EducationEntry], str]:
    """Extract structured education entries from normalized text.

    Returns:
        Tuple of (education_entries, status)
        where status is 'identified', 'unknown', or 'confirmed_absent' (EC-08).
    """
    if CONFIRMED_ABSENCE_EDU.search(text):
        return [], "confirmed_absent"

    entries: List[EducationEntry] = []
    lines = text.split("\n")

    for idx, line in enumerate(lines):
        detected_degree: Optional[str] = None
        for degree_name, pattern in DEGREE_PATTERNS:
            if pattern.search(line):
                detected_degree = degree_name
                break

        has_institution = bool(UNIVERSITY_KEYWORDS.search(line))

        if detected_degree or has_institution:
            # Check broader surrounding context window for full educational record
            context_start = max(0, idx - 2)
            context_end = min(len(lines), idx + 4)
            block = " ".join(lines[context_start:context_end])

            # Detect field of study
            detected_field: Optional[str] = None
            for field in FIELDS_OF_STUDY:
                if re.search(rf"\b{re.escape(field)}\b", block, re.IGNORECASE):
                    detected_field = field
                    break

            # Detect institution name
            detected_inst: Optional[str] = None
            inst_regex = re.compile(
                r"((?:University|College|Institute|Academy|Polytechnic)[A-Za-z0-9\s,&'-]*|[A-Z][A-Za-z0-9\s,&'-]*(?:University|College|Institute|Academy|Polytechnic)[A-Za-z0-9\s,&'-]*)",
            )
            # Search current line and adjacent lines
            for l_candidate in lines[max(0, idx - 1):min(len(lines), idx + 3)]:
                m = inst_regex.search(l_candidate)
                if m:
                    cand_text = m.group(1).strip()
                    # Filter out short or false positive phrases
                    if len(cand_text) > 6 and UNIVERSITY_KEYWORDS.search(cand_text):
                        detected_inst = cand_text
                        break

            # Detect graduation year (1970 - 2035)
            grad_year: Optional[int] = None
            year_match = re.search(r"\b(19[7-9]\d|20[0-3]\d)\b", block)
            if year_match:
                grad_year = int(year_match.group(1))

            entry = EducationEntry(
                degree=detected_degree,
                field_of_study=detected_field,
                institution=detected_inst,
                graduation_year=grad_year,
                evidence_snippet=block[:250].strip(),
            )

            # Avoid adding duplicate entries for the same degree and institution
            is_duplicate = any(
                e.degree == entry.degree
                and e.institution == entry.institution
                and (e.graduation_year == entry.graduation_year or entry.graduation_year is None)
                for e in entries
            )
            if not is_duplicate:
                entries.append(entry)

    status = "identified" if len(entries) > 0 else "unknown"
    return entries, status


def extract_experience_summary(text: str) -> ExperienceSummary:
    """Extract explicitly stated total years of experience, distinguishing unknown from confirmed absence (EC-08)."""
    # 1. Check for confirmed absence of experience
    if CONFIRMED_ABSENCE_EXP.search(text):
        match = CONFIRMED_ABSENCE_EXP.search(text)
        snippet = match.group(0) if match else None
        return ExperienceSummary(
            explicit_years_of_experience=0.0,
            status="confirmed_absent",
            evidence_snippet=snippet,
        )

    # 2. Check for explicitly stated tenure
    for pattern in EXPLICIT_EXP_PATTERNS:
        match = pattern.search(text)
        if match:
            years_str = match.group(1)
            try:
                years = float(years_str)
                start, end = match.span()
                snippet = extract_evidence_snippet(text, start, end, window_words=15)
                return ExperienceSummary(
                    explicit_years_of_experience=years,
                    status="identified",
                    evidence_snippet=snippet,
                )
            except ValueError:
                pass

    # 3. Check for work history date ranges to derive calendar tenure without fabrication
    ranges = _DATE_RANGE_PATTERN.findall(text)
    if ranges:
        total_derived_years = 0.0
        current_year = 2026  # Anchored to system operational year
        intervals = []
        for start_yr_str, end_val in ranges:
            try:
                start_yr = int(start_yr_str)
                if not end_val or end_val.lower() in ("present", "current", "now"):
                    end_yr = current_year
                else:
                    end_yr = int(end_val)
                if 1970 <= start_yr <= end_yr <= current_year + 5:
                    intervals.append((start_yr, end_yr))
            except ValueError:
                continue

        if intervals:
            # Union of overlapping intervals to prevent double-counting concurrent roles (EC-20)
            intervals.sort(key=lambda x: x[0])
            merged = [intervals[0]]
            for current in intervals[1:]:
                prev_start, prev_end = merged[-1]
                if current[0] <= prev_end:
                    merged[-1] = (prev_start, max(prev_end, current[1]))
                else:
                    merged.append(current)

            total_derived_years = sum(end - start for start, end in merged)
            if total_derived_years > 0:
                return ExperienceSummary(
                    explicit_years_of_experience=float(total_derived_years),
                    status="identified",
                    evidence_snippet=f"Derived from chronological tenure: {len(merged)} employment period(s).",
                )

    # 4. Unknown tenure (EC-08)
    return ExperienceSummary(
        explicit_years_of_experience=None,
        status="unknown",
        evidence_snippet=None,
    )


def extract_roles(text: str) -> Tuple[List[RoleEntry], str]:
    """Extract chronological work experiences and roles from normalized text.

    Returns:
        Tuple of (roles, status)
    """
    roles: List[RoleEntry] = []
    lines = text.split("\n")

    current_title: Optional[str] = None
    current_company: Optional[str] = None
    current_duration: Optional[str] = None
    current_desc_lines: List[str] = []

    for line in lines:
        title_match = _JOB_TITLES_PATTERN.search(line)
        date_match = _DATE_RANGE_PATTERN.search(line)

        if title_match:
            # If an existing role is pending, save it
            if current_title:
                roles.append(
                    RoleEntry(
                        title=current_title,
                        company=current_company,
                        duration=current_duration,
                        description=" ".join(current_desc_lines).strip()[:400],
                        evidence_snippet=f"{current_title} at {current_company or 'Company'} ({current_duration or 'Dates'})",
                    )
                )
                current_desc_lines = []

            current_title = title_match.group(0).strip()

            # Attempt to extract company and date from the same line or context
            company_match = re.search(r"(?:at|@|,|\||[-–—])\s+([A-Z][A-Za-z0-9\s&]+?)(?:\s*[-–—|,\(]|$)", line)
            current_company = company_match.group(1).strip() if company_match else None
            current_duration = date_match.group(0).strip() if date_match else None

        elif date_match and current_title and not current_duration:
            current_duration = date_match.group(0).strip()

        elif current_title and line.strip().startswith(("-", "*", "•", "–")):
            # Role bullet point description
            current_desc_lines.append(line.strip().lstrip("-*•– "))

        elif current_title and len(current_desc_lines) < 3 and len(line.strip()) > 20:
            current_desc_lines.append(line.strip())

    if current_title:
        roles.append(
            RoleEntry(
                title=current_title,
                company=current_company,
                duration=current_duration,
                description=" ".join(current_desc_lines).strip()[:400],
                evidence_snippet=f"{current_title} at {current_company or 'Company'} ({current_duration or 'Dates'})",
            )
        )

    status = "identified" if len(roles) > 0 else "unknown"
    return roles, status
