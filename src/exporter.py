"""
exporter.py

Exports ranked candidate results to CSV and JSON.

Features
--------
- Creates output directory automatically.
- Exports recruiter-friendly CSV.
- Exports detailed JSON.
- Handles missing fields safely.
- Logs export status.
"""

import csv
import json
from pathlib import Path

from utils import logger


CSV_FIELDS = [
    "rank",
    "file",
    "name",
    "email",
    "phone",
    "github",
    "linkedin",
    "portfolio",
    "score",
    "tier",
    "semantic_similarity",
    "skill_match_pct",
    "experience_match_pct",
    "education_match_pct",
    "education",
    "years_experience",
    "matched_skills",
    "missing_skills",
    "reasoning",
]


def export_json(results: list, out_path: Path) -> None:
    """
    Export ranked candidates to JSON.
    """

    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(
                results,
                f,
                indent=4,
                ensure_ascii=False,
            )

        logger.info(f"JSON exported successfully -> {out_path}")

    except Exception as e:
        logger.error(f"Failed to export JSON: {e}")


def export_csv(results: list, out_path: Path) -> None:
    """
    Export ranked candidates to CSV.
    """

    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(
            out_path,
            "w",
            newline="",
            encoding="utf-8",
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=CSV_FIELDS,
                extrasaction="ignore",
            )

            writer.writeheader()

            for candidate in results:

                row = dict(candidate)

                row["matched_skills"] = ", ".join(
                    row.get("matched_skills", [])
                )

                row["missing_skills"] = ", ".join(
                    row.get("missing_skills", [])
                )

                # Fill missing optional fields
                row.setdefault("github", "")
                row.setdefault("linkedin", "")
                row.setdefault("portfolio", "")
                row.setdefault("phone", "")
                row.setdefault("email", "")

                writer.writerow(row)

        logger.info(f"CSV exported successfully -> {out_path}")

    except Exception as e:
        logger.error(f"Failed to export CSV: {e}")