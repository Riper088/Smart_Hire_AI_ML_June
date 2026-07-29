"""Unsupervised content-based recommender: cosine-similarity job ranking (top-N)."""

import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src import config
from src.data.preprocess import clean_text

JOB_VECTORIZER_PATH = config.MODELS_DIR / "job_vectorizer.pkl"
JOB_MATRIX_PATH = config.MODELS_DIR / "job_matrix.pkl"

def train_and_save():
    """Compute TF-IDF matrix for jobs and save it."""
    print(f"Loading {config.JOBS_CLEAN_CSV}...")
    df = pd.read_csv(config.JOBS_CLEAN_CSV)
    df = df.dropna(subset=["text"])
    
    vectorizer = TfidfVectorizer(max_features=10000, stop_words="english")
    job_matrix = vectorizer.fit_transform(df["text"])
    
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, JOB_VECTORIZER_PATH)
    joblib.dump(job_matrix, JOB_MATRIX_PATH)
    print(f"Saved job recommender models to {config.MODELS_DIR}")

def recommend_jobs(resume_text: str, top_n: int = config.TOP_N) -> pd.DataFrame:
    """Recommend top_n jobs for a given resume text."""
    if not JOB_VECTORIZER_PATH.exists() or not JOB_MATRIX_PATH.exists():
        raise FileNotFoundError("Models not found. Run train_and_save() first.")
        
    df = pd.read_csv(config.JOBS_CLEAN_CSV)
    df = df.dropna(subset=["text"]).reset_index(drop=True)
    
    vectorizer = joblib.load(JOB_VECTORIZER_PATH)
    job_matrix = joblib.load(JOB_MATRIX_PATH)
    
    cleaned = clean_text(resume_text)
    resume_vector = vectorizer.transform([cleaned])
    
    sim_scores = cosine_similarity(resume_vector, job_matrix).flatten()
    top_indices = sim_scores.argsort()[-top_n:][::-1]
    
    results = df.iloc[top_indices].copy()
    results["similarity_score"] = sim_scores[top_indices]
    
    return results

if __name__ == "__main__":
    train_and_save()
