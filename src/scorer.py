"""
scorer.py

Ranks candidates by combining:

- Semantic Similarity
- Skill Match
- Experience Match
- Education Match

Outputs:
- Final Score (0-100)
- Candidate Tier
- Matched Skills
- Missing Skills
- Human-readable reasoning
"""

from config import WEIGHTS, TIER_THRESHOLDS
from similarity import compute_semantic_similarity


# ------------------------------------------------------------------
# Skill Match
# ------------------------------------------------------------------

def _skill_match_score(candidate_skills: list, jd_skills: list):
    """
    Returns:
        score (0-1),
        matched skills,
        missing skills
    """

    if not jd_skills:
        return 1.0, [], []

    jd = set(jd_skills)
    candidate = set(candidate_skills)

    matched = sorted(jd & candidate)
    missing = sorted(jd - candidate)

    score = len(matched) / len(jd)

    return score, matched, missing


# ------------------------------------------------------------------
# Experience Match
# ------------------------------------------------------------------

def _experience_score(candidate_years: float, jd_years: float):

    if jd_years <= 0:
        return 1.0

    if candidate_years >= jd_years:
        return 1.0

    return max(0.0, candidate_years / jd_years)


# ------------------------------------------------------------------
# Education Match
# ------------------------------------------------------------------

def _education_score(candidate_education: str, jd_education: str):

    if not jd_education or jd_education == "Not specified":
        return 1.0

    if not candidate_education:
        return 0.0

    candidate = candidate_education.lower()
    required = jd_education.lower()

    if candidate == required:
        return 1.0

    if required in candidate:
        return 1.0

    return 0.5


# ------------------------------------------------------------------
# Tier
# ------------------------------------------------------------------

def _tier(score):

    for tier, threshold in TIER_THRESHOLDS.items():

        if score >= threshold:
            return tier

    return "Weak Match"


# ------------------------------------------------------------------
# Reasoning
# ------------------------------------------------------------------

def _build_reasoning(
    matched,
    missing,
    sim_score,
    exp_score,
    edu_score,
    candidate_years,
    jd_years,
    candidate_education,
    jd_education,
):

    parts = []

    if matched:
        parts.append(
            f"Matched {len(matched)} skill(s): {', '.join(matched)}."
        )
    else:
        parts.append("No required skills matched.")

    if missing:
        parts.append(
            f"Missing skills: {', '.join(missing)}."
        )

    parts.append(
        f"Semantic similarity: {sim_score:.0%}."
    )

    if jd_years > 0:
        parts.append(
            f"Experience: {candidate_years:g} yrs "
            f"(Required {jd_years:g} yrs, Match {exp_score:.0%})."
        )
    else:
        parts.append(
            f"Experience: {candidate_years:g} yrs."
        )

    parts.append(
        f"Education: {candidate_education} "
        f"(Required: {jd_education}, Match {edu_score:.0%})."
    )

    return " ".join(parts)


# ------------------------------------------------------------------
# Main Scoring Function
# ------------------------------------------------------------------

def score_candidates(jd_profile: dict, candidate_profiles: list):

    resume_texts = [
        c["raw_text"]
        for c in candidate_profiles
    ]

    similarity_scores = compute_semantic_similarity(
        jd_profile["raw_text"],
        resume_texts,
    )

    results = []

    for candidate, sim_score in zip(candidate_profiles, similarity_scores):

        skill_score, matched, missing = _skill_match_score(
            candidate["skills"],
            jd_profile["skills"],
        )

        exp_score = _experience_score(
            candidate["years_experience"],
            jd_profile["years_experience"],
        )

        edu_score = _education_score(
            candidate["education"],
            jd_profile["education"],
        )

        final_score = (
            WEIGHTS["semantic_similarity"] * sim_score
            + WEIGHTS["skill_match"] * skill_score
            + WEIGHTS["experience_match"] * exp_score
            + WEIGHTS["education_match"] * edu_score
        )

        final_score = round(final_score * 100, 2)

        profile = dict(candidate)
        profile.pop("raw_text", None)

        profile.update({
            "score": final_score,
            "tier": _tier(final_score),
            "semantic_similarity": round(sim_score * 100, 2),
            "skill_match_pct": round(skill_score * 100, 2),
            "experience_match_pct": round(exp_score * 100, 2),
            "education_match_pct": round(edu_score * 100, 2),
            "matched_skills": matched,
            "missing_skills": missing,
            "reasoning": _build_reasoning(
                matched,
                missing,
                sim_score,
                exp_score,
                edu_score,
                candidate["years_experience"],
                jd_profile["years_experience"],
                candidate["education"],
                jd_profile["education"],
            ),
        })

        results.append(profile)

    results.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    for rank, candidate in enumerate(results, start=1):
        candidate["rank"] = rank

    return results