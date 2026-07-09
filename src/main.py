"""
main.py

Entry point for the Resume Screening Agent.

Pipeline
--------
1. Load Job Description
2. Load Resume Files
3. Extract Candidate Information
4. Score Candidates
5. Export Results
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import JD_DIR, OUTPUT_DIR, RESUME_DIR
from exporter import export_csv, export_json
from extractor import (
    extract_candidate_profile,
    extract_jd_requirements,
)
from parser import load_resumes, parse_resume
from scorer import score_candidates
from utils import logger


# ----------------------------------------------------------
# Command Line Arguments
# ----------------------------------------------------------

def parse_args():

    parser = argparse.ArgumentParser(
        description="AI Resume Screening Agent"
    )

    parser.add_argument(
        "--jd",
        type=str,
        default=None,
        help="Path to Job Description file (.txt/.pdf/.docx).",
    )

    parser.add_argument(
        "--resumes",
        type=str,
        default=str(RESUME_DIR),
        help="Folder containing resumes.",
    )

    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Top N candidates to display.",
    )

    parser.add_argument(
        "--out-prefix",
        type=str,
        default="ranked_candidates",
        help="Output filename prefix.",
    )

    return parser.parse_args()


# ----------------------------------------------------------
# Resolve JD
# ----------------------------------------------------------

def resolve_jd_path(jd_arg):

    if jd_arg:

        path = Path(jd_arg)

        if not path.exists():
            raise FileNotFoundError(f"JD not found: {path}")

        return path

    candidates = sorted(JD_DIR.glob("*"))

    candidates = [
        file
        for file in candidates
        if file.is_file()
    ]

    if not candidates:
        raise FileNotFoundError(
            f"No Job Description found inside {JD_DIR}"
        )

    return candidates[0]


# ----------------------------------------------------------
# Print Results
# ----------------------------------------------------------

def print_shortlist(results, top_n):

    total = len(results)

    print("\n")
    print("=" * 90)
    print(f"TOP {min(top_n, total)} CANDIDATES")
    print("=" * 90)

    for candidate in results[:top_n]:

        print(f"\nRank        : {candidate['rank']}")
        print(f"Name        : {candidate['name']}")
        print(f"Score       : {candidate['score']}/100")
        print(f"Tier        : {candidate['tier']}")
        print(f"Resume      : {candidate['file']}")

        if candidate.get("email"):
            print(f"Email       : {candidate['email']}")

        if candidate.get("phone"):
            print(f"Phone       : {candidate['phone']}")

        if candidate.get("github"):
            print(f"GitHub      : {candidate['github']}")

        if candidate.get("linkedin"):
            print(f"LinkedIn    : {candidate['linkedin']}")

        if candidate.get("portfolio"):
            print(f"Portfolio   : {candidate['portfolio']}")

        print(f"Education   : {candidate['education']}")
        print(f"Experience  : {candidate['years_experience']} years")

        print(
            "Matched     : "
            + (
                ", ".join(candidate["matched_skills"])
                if candidate["matched_skills"]
                else "None"
            )
        )

        print(
            "Missing     : "
            + (
                ", ".join(candidate["missing_skills"])
                if candidate["missing_skills"]
                else "None"
            )
        )

        print(f"Reason      : {candidate['reasoning']}")

        print("-" * 90)


# ----------------------------------------------------------
# Main
# ----------------------------------------------------------

def main():

    start = time.time()

    logger.info("=" * 70)
    logger.info("Resume Screening Agent Started")
    logger.info("=" * 70)

    args = parse_args()

    # ----------------------------
    # Step 1
    # ----------------------------

    logger.info("Step 1/5 : Loading Job Description")

    jd_path = resolve_jd_path(args.jd)

    logger.info(f"Using JD : {jd_path.name}")

    jd_text = parse_resume(jd_path)

    if not jd_text.strip():
        raise ValueError("Unable to extract text from Job Description.")

    jd_profile = extract_jd_requirements(jd_text)

    # ----------------------------
    # Step 2
    # ----------------------------

    logger.info("Step 2/5 : Loading Resumes")

    resume_folder = Path(args.resumes)

    if not resume_folder.exists():
        raise FileNotFoundError(
            f"Resume folder not found: {resume_folder}"
        )

    resume_texts = load_resumes(resume_folder)

    if not resume_texts:
        raise ValueError("No resumes found.")

    logger.info(f"Loaded {len(resume_texts)} resumes.")

    # ----------------------------
    # Step 3
    # ----------------------------

    logger.info("Step 3/5 : Extracting Profiles")

    candidate_profiles = []

    for filename, text in resume_texts.items():

        try:

            logger.info(f"Processing {filename}")

            profile = extract_candidate_profile(
                filename,
                text,
            )

            candidate_profiles.append(profile)

        except Exception as e:

            logger.warning(
                f"Skipping {filename} : {e}"
            )

    # ----------------------------
    # Step 4
    # ----------------------------

    logger.info("Step 4/5 : Scoring Candidates")

    results = score_candidates(
        jd_profile,
        candidate_profiles,
    )

    # ----------------------------
    # Step 5
    # ----------------------------

    logger.info("Step 5/5 : Exporting Results")

    csv_path = OUTPUT_DIR / f"{args.out_prefix}.csv"
    json_path = OUTPUT_DIR / f"{args.out_prefix}.json"

    export_csv(results, csv_path)
    export_json(results, json_path)

    print_shortlist(results, args.top)

    logger.info(f"CSV Report  : {csv_path}")
    logger.info(f"JSON Report : {json_path}")

    elapsed = time.time() - start

    logger.info("=" * 70)
    logger.info(f"Completed Successfully in {elapsed:.2f} seconds")
    logger.info("=" * 70)


# ----------------------------------------------------------
# Run
# ----------------------------------------------------------

if __name__ == "__main__":

    try:

        main()

    except FileNotFoundError as e:

        logger.error(e)

    except ValueError as e:

        logger.error(e)

    except KeyboardInterrupt:

        logger.warning("Execution Cancelled.")

    except Exception as e:

        logger.exception(e)