"""
config.py
Central configuration for the Resume Screening Agent.

Keeping all tunables in one place makes the scoring behavior easy to
audit and adjust without touching the pipeline logic.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

RESUME_DIR = DATA_DIR / "resumes"
JD_DIR = DATA_DIR / "job_description"
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Scoring weights (must sum to 1.0)
# ---------------------------------------------------------------------------
WEIGHTS = {
    "semantic_similarity": 0.20,
    "skill_match": 0.40,
    "experience_match": 0.20,
    "education_match": 0.20,
}

assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-6, "WEIGHTS must sum to 1.0"

# ---------------------------------------------------------------------------
# Skill taxonomy
# ---------------------------------------------------------------------------
SKILL_TAXONOMY = [
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go",
    "rust", "sql", "r", "scala", "kotlin", "swift", "php",

    # AI / ML
    "machine learning", "deep learning", "nlp",
    "natural language processing", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn",
    "pandas", "numpy", "statistics",
    "data analysis", "data science",
    "llm", "large language models",
    "generative ai", "prompt engineering",
    "rag", "retrieval augmented generation",

    # Web Development
    "html", "css", "react", "node.js",
    "django", "flask", "fastapi",
    "rest api", "graphql", "microservices",

    # Cloud / DevOps
    "aws", "azure", "gcp",
    "docker", "kubernetes",
    "terraform", "ci/cd",
    "linux", "git", "devops",

    # Data Engineering
    "spark", "kafka", "airflow",
    "etl", "data pipeline", "hadoop",

    # Databases
    "mysql", "postgresql",
    "mongodb", "redis",
    "elasticsearch",

    # Analytics
    "excel", "power bi", "tableau",

    # Soft Skills
    "communication",
    "leadership",
    "agile",
    "scrum",
    "project management",
    "business analysis",
    "product management",
    "stakeholder management",
]

# ---------------------------------------------------------------------------
# Education Levels
# ---------------------------------------------------------------------------
EDUCATION_LEVELS = [
    ("high school", 1),
    ("diploma", 2),
    ("associate degree", 2),

    ("bachelor", 3),
    ("b.tech", 3),
    ("b.e.", 3),
    ("bsc", 3),
    ("b.sc", 3),

    ("master", 4),
    ("m.tech", 4),
    ("mba", 4),
    ("msc", 4),
    ("m.sc", 4),

    ("phd", 5),
    ("ph.d", 5),
    ("doctorate", 5),
]

# ---------------------------------------------------------------------------
# Supported Resume Formats
# ---------------------------------------------------------------------------
SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
}

# ---------------------------------------------------------------------------
# Candidate Score Tiers
# ---------------------------------------------------------------------------
TIER_THRESHOLDS = {
    "Excellent Match": 90,
    "Strong Match": 75,
    "Good Match": 60,
    "Possible Match": 45,
}