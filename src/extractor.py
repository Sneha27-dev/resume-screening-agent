"""
extractor.py

Extracts structured information from resumes and job descriptions.

Features
--------
- Name
- Email
- Phone
- GitHub
- LinkedIn
- Portfolio
- Skills
- Education
- Experience

Uses a rule-based approach for speed, explainability,
and zero ML dependencies.
"""

import re

from config import SKILL_TAXONOMY, EDUCATION_LEVELS
from utils import (
    find_email,
    find_phone,
    find_name,
    extract_years_of_experience,
    logger,
)

# --------------------------------------------------------------------
# Negation Detection
# --------------------------------------------------------------------

_NEGATION_WORDS = {
    "no",
    "not",
    "without",
    "none",
    "lacks",
    "lacking",
}

_NEGATION_WINDOW = 3


def _is_negated(probe: str, match_start: int) -> bool:
    """
    Check whether a skill mention is negated.
    Example:
    "No Python experience"
    """

    preceding = probe[:match_start].split()

    window = preceding[-_NEGATION_WINDOW:]

    return any(
        word.strip(".,;:!?").lower() in _NEGATION_WORDS
        for word in window
    )


# --------------------------------------------------------------------
# URL Extraction
# --------------------------------------------------------------------

def extract_github(text: str) -> str:
    """
    Extract GitHub profile.
    """

    match = re.search(
        r"https?://(?:www\.)?github\.com/[A-Za-z0-9_.-]+/?",
        text,
        re.IGNORECASE,
    )

    return match.group(0).rstrip("/") if match else ""


def extract_linkedin(text: str) -> str:
    """
    Extract LinkedIn profile.
    """

    match = re.search(
        r"https?://(?:www\.)?linkedin\.com/[^\s]+",
        text,
        re.IGNORECASE,
    )

    return match.group(0).rstrip("/") if match else ""


def extract_portfolio(text: str) -> str:
    """
    Extract personal portfolio website.
    Ignores GitHub and LinkedIn.
    """

    urls = re.findall(
        r"https?://[^\s]+",
        text,
        re.IGNORECASE,
    )

    ignored = (
        "github.com",
        "linkedin.com",
    )

    for url in urls:

        if not any(site in url.lower() for site in ignored):
            return url.rstrip(").,;")

    return ""


# --------------------------------------------------------------------
# Skill Extraction
# --------------------------------------------------------------------

def extract_skills(text: str) -> list:
    """
    Extract skills from resume using the configured taxonomy.
    """

    if not text:
        return []

    probe = text.lower()

    probe = (
        probe.replace("\n", " ")
        .replace(",", " ")
        .replace("/", " ")
        .replace(";", " ")
        .replace("(", " ")
        .replace(")", " ")
    )

    probe = re.sub(r"\.(?=\s|$)", " ", probe)

    probe = f" {probe} "

    found = set()

    for skill in SKILL_TAXONOMY:

        pattern = rf"\b{re.escape(skill.lower())}\b"

        match = re.search(pattern, probe)

        if match and not _is_negated(probe, match.start()):
            found.add(skill)

    skills = sorted(found)

    logger.info(f"Extracted {len(skills)} skill(s).")

    return skills


# --------------------------------------------------------------------
# Education Extraction
# --------------------------------------------------------------------

def extract_education(text: str) -> str:
    """
    Return the highest education level found.
    """

    if not text:
        return "Not specified"

    text = text.lower()

    highest = "Not specified"
    rank = 0

    for education, value in EDUCATION_LEVELS:

        if education in text and value > rank:
            highest = education.upper()
            rank = value

    return highest


# --------------------------------------------------------------------
# Candidate Profile
# --------------------------------------------------------------------

def extract_candidate_profile(filename: str, text: str) -> dict:
    """
    Convert a resume into a structured candidate profile.
    """

    profile = {
        "file": filename,
        "name": find_name(text),
        "email": find_email(text),
        "phone": find_phone(text),
        "github": extract_github(text),
        "linkedin": extract_linkedin(text),
        "portfolio": extract_portfolio(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "years_experience": extract_years_of_experience(text),
        "raw_text": text,
    }

    logger.info(
        f"{profile['name']} -> "
        f"{len(profile['skills'])} skills extracted."
    )

    return profile


# --------------------------------------------------------------------
# Job Description Profile
# --------------------------------------------------------------------

def extract_jd_requirements(jd_text: str) -> dict:
    """
    Convert Job Description into a structured profile.
    """

    profile = {
        "skills": extract_skills(jd_text),
        "education": extract_education(jd_text),
        "years_experience": extract_years_of_experience(jd_text),
        "raw_text": jd_text,
    }

    logger.info(
        f"JD contains {len(profile['skills'])} required skills."
    )

    return profile