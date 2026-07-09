"""
similarity.py

Computes semantic similarity between a Job Description and resumes
using TF-IDF + Cosine Similarity.

Advantages
----------
- Runs completely offline
- No API key required
- Fast and lightweight
- Deterministic and explainable
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils import logger


def compute_semantic_similarity(jd_text: str, resume_texts: list) -> list:
    """
    Compute cosine similarity between the Job Description
    and each resume.

    Parameters
    ----------
    jd_text : str
        Job description text.

    resume_texts : list[str]
        List of resume texts.

    Returns
    -------
    list[float]
        Similarity scores between 0 and 1.
    """

    if not resume_texts:
        logger.warning("No resumes supplied for similarity computation.")
        return []

    corpus = [jd_text] + resume_texts

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
        )

        tfidf_matrix = vectorizer.fit_transform(corpus)

        jd_vector = tfidf_matrix[0:1]
        resume_vectors = tfidf_matrix[1:]

        similarities = cosine_similarity(
            jd_vector,
            resume_vectors,
        )[0]

        logger.info(
            f"Computed semantic similarity for {len(resume_texts)} resume(s)."
        )

        return similarities.tolist()

    except Exception as e:
        logger.exception(f"Semantic similarity computation failed: {e}")
        raise