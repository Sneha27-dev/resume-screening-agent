"""
utils.py

Shared helper functions for the Resume Screening Agent.
"""

import logging
import re

# ------------------------------------------------------------------
# Logger
# ------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)

logger = logging.getLogger("resume-agent")


# ------------------------------------------------------------------
# Text Cleaning
# ------------------------------------------------------------------

def clean_text(text: str) -> str:
    """
    Normalize extracted text.
    """

    if not text:
        return ""

    text = text.replace("\x00", " ")
    text = text.replace("\r", "\n")

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)

    return text.strip()


# ------------------------------------------------------------------
# Email
# ------------------------------------------------------------------

def find_email(text: str) -> str:

    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text,
    )

    return match.group(0) if match else ""


# ------------------------------------------------------------------
# Phone
# ------------------------------------------------------------------

def find_phone(text: str) -> str:

    match = re.search(
        r"(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3,5}\)?[\s-]?)?\d{3,5}[\s-]?\d{4}",
        text,
    )

    return match.group(0).strip() if match else ""


# ------------------------------------------------------------------
# Name
# ------------------------------------------------------------------

def find_name(text: str) -> str:
    """
    Simple heuristic:
    The candidate's name usually appears in the first few lines.
    """

    lines = text.splitlines()

    for line in lines[:10]:

        line = line.strip()

        if not line:
            continue

        if "@" in line:
            continue

        if re.search(r"\d{4,}", line):
            continue

        words = line.split()

        if (
            2 <= len(words) <= 4
            and all(
                w.replace(".", "").replace("-", "").isalpha()
                for w in words
            )
        ):
            return line.title()

    return "Unknown Candidate"


# ------------------------------------------------------------------
# Experience
# ------------------------------------------------------------------

def extract_years_of_experience(text: str) -> float:
    """
    Extract the highest mentioned years of experience.
    """

    text = text.lower()

    matches = re.findall(
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
        text,
    )

    if not matches:
        return 0.0

    years = [float(x) for x in matches]

    return max(years)