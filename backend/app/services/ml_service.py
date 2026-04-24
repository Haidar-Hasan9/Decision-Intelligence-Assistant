import logging
from functools import lru_cache
import joblib
import os
import pandas as pd
import numpy as np
from app.config import settings as cfg
from .feature_engineering import compute_features

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def load_model():
    """Load the trained pipeline (preprocessor + classifier)."""
    pipeline_path = os.path.join(os.path.dirname(__file__), "..", "..", "models", "priority_classifier_pipeline.joblib")
    return joblib.load(pipeline_path)

@lru_cache(maxsize=1)
def load_model_metadata():
    """Load the model metadata (test scores, etc)."""
    meta_path = os.path.join(os.path.dirname(__file__), "..", "..", "models", "model_metadata.joblib")
    return joblib.load(meta_path)

def predict_priority(text: str):
    """
    Predict priority for a single tweet text.
    Returns {"priority": 0 or 1, "confidence": float}
    """
    model = load_model()
    # Compute features as a list
    features = compute_features(text)

    # Column names must match exactly those used during training (look at `feature_cols` from notebook)
    feature_cols = [
        'text_length', 'word_count', 'exclamation_count', 'question_count',
        'all_caps_ratio', 'sentiment_polarity', 'sentiment_subjectivity', 'has_urgent_keyword'
    ]

    # Wrap features into a DataFrame (required by ColumnTransformer)
    df = pd.DataFrame([features], columns=feature_cols)

    pred = model.predict(df)[0]
    proba = model.predict_proba(df)[0]
    confidence = proba[1] if pred == 1 else proba[0]
    return {"priority": int(pred), "confidence": float(confidence)}