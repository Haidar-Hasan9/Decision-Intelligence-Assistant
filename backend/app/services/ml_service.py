import pandas as pd
import logging
from functools import lru_cache
import joblib
import os
import numpy as np
from app.config import settings as cfg
from .feature_engineering import compute_features  # we'll define this next

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def load_model():
    """Load the trained pipeline (preprocessor + classifier)."""
    pipeline_path = os.path.join(os.path.dirname(__file__), "..", "..", "models", "priority_classifier_pipeline.joblib")
    return joblib.load(pipeline_path)

def predict_priority(text: str):
    """
    Predict priority for a single tweet text.
    Returns {"priority": 0 or 1, "confidence": float}
    """
    model = load_model()

    # Compute features (returns a list)
    features_list = compute_features(text)
    
    # Must match the training feature names and order
    feature_names = [
        'text_length', 'word_count', 'exclamation_count', 'question_count',
        'all_caps_ratio', 'sentiment_polarity', 'sentiment_subjectivity', 'has_urgent_keyword'
    ]
    
    # Create a DataFrame because the pipeline was trained with named columns
    features_df = pd.DataFrame([features_list], columns=feature_names)
    pred = model.predict(features_df)[0]
    proba = model.predict_proba(features_df)[0]  # [prob_class0, prob_class1]
    confidence = proba[1] if pred == 1 else proba[0]
    return {"priority": int(pred), "confidence": float(confidence)}