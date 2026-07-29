"""Supervised resume category classifier (train / predict / save / load)."""

import pandas as pd
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from src import config
from src.data.preprocess import clean_text

CLASSIFIER_PATH = config.MODELS_DIR / "classifier.pkl"
VECTORIZER_PATH = config.MODELS_DIR / "vectorizer.pkl"


def train_and_save():
    """Train the classifier and save to models/."""
    print(f"Loading {config.RESUMES_CLEAN_CSV}...")
    df = pd.read_csv(config.RESUMES_CLEAN_CSV)
    df = df.dropna(subset=["text", "Category"])
    
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words="english")
    X = vectorizer.fit_transform(df["text"])
    y = df["Category"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=config.RANDOM_STATE, stratify=y)
    
    clf = LogisticRegression(max_iter=1000, class_weight='balanced')
    clf.fit(X_train, y_train)
    
    print("Evaluating...")
    print(classification_report(y_test, clf.predict(X_test)))
    
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, CLASSIFIER_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"Saved models to {config.MODELS_DIR}")


def predict_category(text: str) -> str:
    """Predict the category for a given resume text."""
    if not CLASSIFIER_PATH.exists() or not VECTORIZER_PATH.exists():
        raise FileNotFoundError("Models not found. Run train_and_save() first.")
        
    clf = joblib.load(CLASSIFIER_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    
    cleaned = clean_text(text)
    features = vectorizer.transform([cleaned])
    pred = clf.predict(features)[0]
    return pred


if __name__ == "__main__":
    train_and_save()
