"""
ai/predict_category.py - Category Inference Engine & Domain Adaptation

Loads the trained TF-IDF + Logistic Regression pipeline and applies an intelligent
hybrid inference approach:
1. Quick domain pattern matching for Indian-style expenses (Swiggy, Zomato, UPI, Auto, Metro, Rent).
2. Machine-learning inference via Scikit-Learn pipeline for broad merchant classification.
3. Fallback to 'Other' with confidence scoring and source tracing.
"""

import os
import re
from pathlib import Path
import joblib

# Global cached model
_MODEL_PIPELINE = None

# Domain Priors for Indian personal expense transactions
INDIAN_DOMAIN_RULES = [
    # Food & Dining
    (r"\b(swiggy|zomato|chai|tea|coffee|samosa|dosa|idli|biryani|pizza|burger|snack|lunch|dinner|breakfast|canteen|food|restaurant|bakery|creamstone|cake|sweet|icecream|hotel)\b", "Food"),
    # Transportation
    (r"\b(metro|auto|ola|uber|rapido|bus|train|irctc|petrol|diesel|fuel|toll|fastag|cab|flight|indigo)\b", "Transportation"),
    # Shopping
    (r"\b(amazon|flipkart|myntra|meesho|clothes|hoodie|shirt|pant|shoes|earphone|mobile|laptop|watch)\b", "Shopping"),
    # Rent & Housing
    (r"\b(rent|room rent|house rent|hostel|brokerage|maintenance)\b", "Rent"),
    # Utilities & Bills
    (r"\b(electricity|water bill|gas|eb bill|broadband|wifi|jio|airtel|vi|recharge|dth|cylinder)\b", "Utilities"),
    # Entertainment & Social
    (r"\b(movie|cinema|pvr|inox|netflix|spotify|prime|hotstar|party|trip|concert|pub|outing|fun)\b", "Entertainment"),
    # Healthcare & Personal Care
    (r"\b(medicine|pharmacy|doctor|hospital|clinic|apollo|medplus|tablet|shampoo|soap|salon|haircut)\b", "Healthcare"),
    # Education
    (r"\b(fee|college|school|exam|reval|arrear|book|tuition|udemy|coursera|course|stationery|xerox)\b", "Education"),
    # Income & Allowances
    (r"\b(from dad|salary|allowance|stipend|cashback|refund|interest|got from|bonus)\b", "Income"),
]


def clean_input_text(text):
    """Normalizes input text identically to training pipeline."""
    if not isinstance(text, str):
        return ""
    t = re.sub(r"^\[(debit|credit)\]\s*", "", text, flags=re.IGNORECASE)
    t = re.sub(r"(PPD|WEB|ACH|TEL|CCD)\s+ID:\s*[\w\d]+", "", t, flags=re.IGNORECASE)
    t = re.sub(r"[^\w\s\*\#]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t.lower()


def get_model():
    """Lazy loader for the trained classification pipeline."""
    global _MODEL_PIPELINE
    if _MODEL_PIPELINE is not None:
        return _MODEL_PIPELINE

    model_paths = [
        os.path.join("ai", "models", "expense_category_model.joblib"),
        os.path.join("models", "expense_category_model.joblib"),
        os.path.join(Path(__file__).resolve().parent, "models", "expense_category_model.joblib"),
    ]

    for p in model_paths:
        if os.path.exists(p):
            try:
                _MODEL_PIPELINE = joblib.load(p)
                return _MODEL_PIPELINE
            except Exception as e:
                print(f"[Warning] Failed loading model at {p}: {e}")

    return None


def predict_category(description):
    """
    Predicts the category for a transaction description.
    Returns:
    {
        "category": str,
        "confidence": float (0.0 to 1.0),
        "source": "Domain Rule Prior" | "AI Model" | "Default",
        "all_probabilities": dict (if AI model available)
    }
    """
    if not description or not str(description).strip():
        return {
            "category": "Other",
            "confidence": 0.0,
            "source": "Default",
            "all_probabilities": {},
        }

    raw_text = str(description).strip().lower()

    # 1. First check domain rules for strong Indian-specific keywords
    for pattern, cat in INDIAN_DOMAIN_RULES:
        if re.search(pattern, raw_text, flags=re.IGNORECASE):
            return {
                "category": cat,
                "confidence": 0.95,
                "source": "Domain Rule Prior",
                "all_probabilities": {cat: 0.95},
            }

    # 2. Machine-Learning Model Prediction
    model = get_model()
    if model is not None:
        cleaned = clean_input_text(description)
        try:
            probs = model.predict_proba([cleaned])[0]
            classes = model.classes_
            best_idx = probs.argmax()
            best_cat = classes[best_idx]
            confidence = float(probs[best_idx])

            # Map US-specific category labels to Application categories if needed
            category_mapping = {
                "Restaurants": "Food",
                "Groceries": "Food",
            }
            app_cat = category_mapping.get(best_cat, best_cat)

            prob_dict = {classes[i]: round(float(probs[i]), 3) for i in range(len(classes))}

            return {
                "category": app_cat,
                "confidence": round(confidence, 3),
                "source": "AI Model",
                "all_probabilities": prob_dict,
            }
        except Exception as e:
            print(f"[Warning] AI prediction failed: {e}")

    # 3. Fallback
    return {
        "category": "Other",
        "confidence": 0.30,
        "source": "Default",
        "all_probabilities": {},
    }
