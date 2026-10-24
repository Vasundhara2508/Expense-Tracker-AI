"""
tests/test_ai.py - AI Category Classification & Prediction Tests
"""

import pytest
from ai.predict_category import predict_category, get_model


def test_ai_model_loaded():
    model = get_model()
    assert model is not None, "Model pipeline should be successfully loaded from joblib"
    assert hasattr(model, "predict")
    assert hasattr(model, "predict_proba")


def test_domain_rule_prior_predictions():
    # Indian-specific domain queries
    res_food = predict_category("Swiggy food order biryani")
    assert res_food["category"] == "Food"
    assert res_food["confidence"] >= 0.80

    res_transport = predict_category("Metro recharge for monthly pass")
    assert res_transport["category"] == "Transportation"
    assert res_transport["confidence"] >= 0.80

    res_income = predict_category("Monthly salary credited from employer")
    assert res_income["category"] == "Income"


def test_ml_model_predictions():
    # Banking descriptions tested against ML model
    res_walmart = predict_category("WAL-MART SUPERCENTER GROCERIES")
    assert res_walmart["category"] in ("Shopping", "Food", "Groceries")
    assert res_walmart["confidence"] > 0.50

    res_netflix = predict_category("NETFLIX MONTHLY SUBSCRIPTION")
    assert res_netflix["category"] in ("Subscription", "Entertainment")
    assert res_netflix["confidence"] > 0.50


def test_empty_description_fallback():
    res = predict_category("")
    assert res["category"] == "Other"
    assert res["confidence"] == 0.0
