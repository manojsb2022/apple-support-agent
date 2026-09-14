"""
classifier.py
Intent classification engine utilizing TF-IDF representations and Linear / Logistic models.
Includes fallbacks and rule heuristics when scikit-learn is not installed.
"""

import math
import os
import pickle
import re
from typing import Dict, List, Tuple, Any

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from src.preprocess import clean_tweet, tokenize

INTENT_KEYWORDS = {
    "battery_issue": ["battery", "drain", "draining", "dying", "overheating", "health", "charge", "charging", "hot"],
    "billing_subscription": ["charged", "charge", "refund", "subscription", "billed", "bill", "payment", "card", "purchase", "renew"],
    "icloud_sync": ["icloud", "sync", "syncing", "photos", "backup", "drive", "storage", "notes", "calendar"],
    "hardware_defect": ["screen", "display", "flicker", "cracked", "broken", "speaker", "camera", "trackpad", "face id", "button", "loose", "port"],
    "software_update": ["update", "ios", "updating", "verify", "verifying", "boot loop", "bricked", "restore", "error code", "patch", "install"],
    "airpods_audio": ["airpod", "airpods", "earbud", "audio", "noise cancellation", "anc", "static", "mic", "sound", "crackling"],
    "account_security": ["apple id", "hacked", "stolen", "locked", "phishing", "unauthorized", "fraud", "password", "two-factor", "2fa"],
    "general_inquiry": ["trade-in", "trade in", "esim", "transfer", "genius bar", "warranty", "store", "order", "delivery", "appointment"]
}


class IntentClassifier:
    def __init__(self):
        self.model = None
        self.classes_ = list(INTENT_KEYWORDS.keys())

    def train_sklearn(self, texts: List[str], labels: List[str]):
        """Train a TF-IDF + LogisticRegression model using scikit-learn."""
        if not SKLEARN_AVAILABLE:
            raise RuntimeError("scikit-learn is required to train via sklearn pipeline.")
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(preprocessor=clean_tweet, ngram_range=(1, 2), max_features=5000)),
            ('clf', LogisticRegression(C=1.0, max_iter=200, random_state=42))
        ])
        pipeline.fit(texts, labels)
        self.model = pipeline
        self.classes_ = list(pipeline.classes_)

    def predict_one(self, text: str) -> Dict[str, Any]:
        """
        Classify text and return predicted intent with confidence scores.
        Uses sklearn model if trained/available, else keyword frequency cosine heuristic.
        """
        if self.model is not None and SKLEARN_AVAILABLE:
            pred = self.model.predict([text])[0]
            probs = self.model.predict_proba([text])[0]
            prob_dict = {cls: float(prob) for cls, prob in zip(self.model.classes_, probs)}
            confidence = prob_dict.get(pred, 0.5)
            return {
                "intent": pred,
                "confidence": round(confidence, 4),
                "probabilities": prob_dict
            }

        # Heuristic / Keyword-based Intent Classifier
        cleaned = clean_tweet(text)
        tokens = set(tokenize(cleaned))
        
        scores = {}
        for intent, kw_list in INTENT_KEYWORDS.items():
            match_count = sum(1 for kw in kw_list if kw in cleaned)
            scores[intent] = match_count

        total_score = sum(scores.values())
        if total_score == 0:
            pred_intent = "general_inquiry"
            confidence = 0.35
            prob_dict = {k: 1.0 / len(INTENT_KEYWORDS) for k in INTENT_KEYWORDS}
        else:
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            pred_intent = sorted_scores[0][0]
            confidence = round(sorted_scores[0][1] / total_score, 4)
            prob_dict = {k: round(v / total_score, 4) for k, v in scores.items()}

        return {
            "intent": pred_intent,
            "confidence": confidence,
            "probabilities": prob_dict
        }

    def predict(self, texts: List[str]) -> List[str]:
        return [self.predict_one(t)["intent"] for t in texts]

    def save(self, filepath: str):
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, filepath: str) -> 'IntentClassifier':
        with open(filepath, 'rb') as f:
            return pickle.load(f)
