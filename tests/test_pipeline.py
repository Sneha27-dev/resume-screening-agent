"""
Basic unit tests for the Resume Screening Agent pipeline.

Run with:  pytest tests/ -v
(run from the project root; conftest.py adds src/ to sys.path)
"""

from extractor import extract_skills, extract_education, extract_candidate_profile
from utils import find_email, find_phone, extract_years_of_experience
from scorer import score_candidates
from extractor import extract_jd_requirements


def test_extract_skills_basic_match():
    text = "Experienced with Python, PyTorch, and SQL for data pipelines."
    skills = extract_skills(text)
    assert "python" in skills
    assert "pytorch" in skills
    assert "sql" in skills


def test_extract_skills_ignores_negated_mentions():
    text = "No machine learning background. Strong in React and JavaScript."
    skills = extract_skills(text)
    assert "machine learning" not in skills
    assert "react" in skills
    assert "javascript" in skills


def test_extract_skills_no_false_positive_substring():
    # "r" should not match inside unrelated words
    text = "Regarding our previous conversation about the report."
    skills = extract_skills(text)
    assert "r" not in skills


def test_extract_education_picks_highest_level():
    text = "I have a Bachelor's degree and later completed a Master's in AI."
    assert extract_education(text) == "MASTER"

def test_extract_years_of_experience():
    assert extract_years_of_experience("5 years of experience in ML") == 5.0
    assert extract_years_of_experience("3.5 yrs experience") == 3.5
    assert extract_years_of_experience("no experience mentioned") == 0.0


def test_find_email():
    assert find_email("Contact me at jane.doe@example.com please") == "jane.doe@example.com"


def test_find_phone():
    assert find_phone("Call me at +91 98765 43210 anytime") != ""


def test_score_candidates_ranks_stronger_resume_higher():
    jd_text = (
        "We need a Python developer with PyTorch, TensorFlow, and AWS "
        "experience. 3+ years of experience required."
    )
    strong_resume = (
        "5 years of experience. Skills: Python, PyTorch, TensorFlow, AWS, "
        "Docker, machine learning."
    )
    weak_resume = (
        "2 years of experience. Skills: Excel, Power BI, communication."
    )

    jd_profile = extract_jd_requirements(jd_text)
    profiles = [
        extract_candidate_profile("strong.txt", strong_resume),
        extract_candidate_profile("weak.txt", weak_resume),
    ]

    results = score_candidates(jd_profile, profiles)

    assert results[0]["file"] == "strong.txt"
    assert results[0]["score"] > results[1]["score"]
    assert results[0]["rank"] == 1
    assert results[1]["rank"] == 2


def test_score_candidates_handles_no_experience_requirement():
    jd_text = "We need someone skilled in Python and SQL."
    resume_text = "Skills: Python, SQL. No years of experience stated."

    jd_profile = extract_jd_requirements(jd_text)
    profiles = [extract_candidate_profile("candidate.txt", resume_text)]

    results = score_candidates(jd_profile, profiles)
    assert results[0]["experience_match_pct"] == 100.0
