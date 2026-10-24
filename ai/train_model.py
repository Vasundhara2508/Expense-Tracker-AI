"""
ai/train_model.py - TF-IDF + Logistic Regression Category Classification Pipeline

Trains a machine-learning text classification pipeline on cleaned transaction descriptions.
Implements:
1. Stratified 80/20 train/test split to prevent data leakage.
2. Text feature extraction using TF-IDF (unigrams & bigrams, sublinear TF scaling).
3. Multinomial Logistic Regression classifier with L2 regularization.
4. Comprehensive evaluation: Accuracy, Precision, Recall, Macro F1, and Confusion Matrix.
5. Model serialization using Joblib to ai/models/expense_category_model.joblib.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)


def train_category_model(
    data_path="data/processed/ai_training_clean.csv",
    model_dir="ai/models",
    test_size=0.20,
    random_state=42,
):
    print("=" * 75)
    print("PHASE 5: TRAINING EXPENSE CATEGORY CLASSIFIER")
    print("=" * 75)

    if not os.path.exists(data_path):
        alt = os.path.join("..", data_path)
        if os.path.exists(alt):
            data_path = alt
        else:
            raise FileNotFoundError(f"Training data not found at {data_path}")

    # 1. Load data
    df = pd.read_csv(data_path)
    print(f"Loaded training dataset: {len(df):,} rows across {df['category'].nunique()} categories.")

    # Use clean_text if available, fallback to description
    text_col = "clean_text" if "clean_text" in df.columns else "description"
    X = df[text_col].astype(str).values
    y = df["category"].astype(str).values

    # 2. Stratified Train/Test Split
    print(f"\n[Split] Splitting data into {int((1-test_size)*100)}% Train and {int(test_size*100)}% Test (Stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    print(f"-> Train samples: {len(X_train):,}")
    print(f"-> Test samples:  {len(X_test):,}")

    # 3. Build Scikit-Learn Pipeline
    print("\n[Pipeline] Constructing TF-IDF Vectorizer + Logistic Regression Pipeline...")
    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=15000,
                sublinear_tf=True,
                token_pattern=r"(?u)\b\w+\b",
            ),
        ),
        (
            "clf",
            LogisticRegression(
                max_iter=1000,
                C=2.5,
                solver="lbfgs",
                random_state=random_state,
            ),
        ),
    ])

    # 4. Train
    print("[Training] Fitting model on training data...")
    pipeline.fit(X_train, y_train)
    print("-> Training completed successfully.")

    # 5. Evaluate on Held-Out Test Set
    print("\n[Evaluation] Evaluating model predictions on held-out test set...")
    y_pred = pipeline.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(
        y_test, y_pred, average="macro", zero_division=0
    )
    prec_weighted, rec_weighted, f1_weighted, _ = precision_recall_fscore_support(
        y_test, y_pred, average="weighted", zero_division=0
    )

    print("\n" + "-" * 50)
    print(f"MODEL PERFORMANCE METRICS (Test Set: {len(X_test):,} records):")
    print("-" * 50)
    print(f"Overall Accuracy:       {acc * 100:.2f}%")
    print(f"Macro Precision:        {prec_macro * 100:.2f}%")
    print(f"Macro Recall:           {rec_macro * 100:.2f}%")
    print(f"Macro F1-Score:         {f1_macro * 100:.2f}%")
    print(f"Weighted F1-Score:      {f1_weighted * 100:.2f}%")
    print("-" * 50)

    # Detailed Per-Category Report
    print("\nDetailed Per-Category Performance:")
    clf_report = classification_report(y_test, y_pred, zero_division=0)
    print(clf_report)

    # 6. Save Model Artifacts
    os.makedirs(model_dir, exist_ok=True)
    model_save_path = os.path.join(model_dir, "expense_category_model.joblib")
    joblib.dump(pipeline, model_save_path)
    print(f"[Saved] Fitted model pipeline saved to: {model_save_path}")

    # Save metrics JSON
    metrics = {
        "accuracy": round(acc, 4),
        "macro_precision": round(prec_macro, 4),
        "macro_recall": round(rec_macro, 4),
        "macro_f1": round(f1_macro, 4),
        "weighted_f1": round(f1_weighted, 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "categories": sorted(list(pipeline.classes_)),
    }
    metrics_path = os.path.join(model_dir, "evaluation_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"[Saved] Evaluation metrics saved to: {metrics_path}")

    print("=" * 75)
    return pipeline, metrics


if __name__ == "__main__":
    train_category_model()
