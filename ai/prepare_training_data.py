"""
ai/prepare_training_data.py - Dataset B Cleaning & ML Data Preparation Pipeline

This script prepares the machine-learning training dataset from DATASET B.csv.
It implements all specifications required for Phase 2 / Phase 5:
1. Loads raw dataset from data/raw/ or root directory.
2. Normalizes whitespace and text formatting across descriptions and labels.
3. Validates and removes any empty or null rows.
4. Identifies and removes exact duplicate rows (22,298 duplicates).
5. Detects and resolves conflicting descriptions mapped to multiple categories.
6. Generates a normalized text feature (stripping debit/credit prefixes and transaction IDs).
7. Analyzes category balance and counts remaining unique descriptions across all 17 classes.
8. Saves cleaned training data to data/processed/ai_training_clean.csv and demo samples.
9. Produces a detailed audit report with recommendations for train/test split to prevent data leakage.
"""

import os
import re
import sys
import pandas as pd
import numpy as np


def find_dataset_b_path():
    """Locate DATASET B.csv in data/raw/ or fallback to workspace root."""
    possible_paths = [
        os.path.join("data", "raw", "DATASET B.csv"),
        "DATASET B.csv",
        os.path.join("..", "data", "raw", "DATASET B.csv"),
        os.path.join("..", "DATASET B.csv"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Could not locate DATASET B.csv. Please ensure it exists in data/raw/ or project root.")


def clean_text_for_nlp(text):
    """
    Normalizes bank transaction text for natural language classification:
    - Removes '[debit]' and '[credit]' prefixes
    - Strips noisy automated transaction ID tails (e.g. 'PPD ID: ...', 'WEB ID: ...')
    - Removes punctuation and extra whitespace
    - Normalizes to lowercase
    """
    if not isinstance(text, str):
        return ""
    # Remove prefix tags
    t = re.sub(r"^\[(debit|credit)\]\s*", "", text, flags=re.IGNORECASE)
    # Remove standard automated banking ID suffixes
    t = re.sub(r"(PPD|WEB|ACH|TEL|CCD)\s+ID:\s*[\w\d]+", "", t, flags=re.IGNORECASE)
    # Remove special characters / extra punctuation but preserve letters & numbers
    t = re.sub(r"[^\w\s\*\#]", " ", t)
    # Collapse consecutive whitespace
    t = re.sub(r"\s+", " ", t).strip()
    return t.lower()


def clean_dataset_b(input_path=None, output_dir="data/processed", sample_dir="data/sample"):
    """
    Execute full cleaning, deduplication, conflict audit, and feature normalization for Dataset B.
    """
    if input_path is None:
        input_path = find_dataset_b_path()

    print("=" * 75)
    print("STEP 2: CLEANING & AUDITING DATASET B (Machine Learning Training Data)")
    print(f"Loading raw file from: {input_path}")
    print("=" * 75)

    # 1. Load raw CSV
    df_raw = pd.read_csv(input_path)
    total_raw_rows = len(df_raw)
    print(f"Loaded {total_raw_rows:,} raw records across columns: {list(df_raw.columns)}\n")

    # 2. Check and report null / empty values
    null_counts = df_raw.isnull().sum()
    print(f"[Audit] Missing values check:\n{null_counts.to_string()}\n")
    df = df_raw.dropna(subset=["description", "category"]).copy()

    # 3. Normalize whitespace
    print("[Transformation] Normalizing whitespace in descriptions and categories...")
    df["description"] = df["description"].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
    df["category"] = df["category"].astype(str).str.strip()

    # Drop any rows that became empty after strip
    df = df[(df["description"] != "") & (df["category"] != "")].copy()

    # 4. Remove exact duplicate rows
    print("\n[Audit] Checking exact duplicate rows...")
    raw_duplicates = df.duplicated(subset=["description", "category"]).sum()
    print(f"-> Exact duplicate rows identified: {raw_duplicates:,} ({(raw_duplicates / total_raw_rows) * 100:.2f}% of raw dataset)")

    df_dedup = df.drop_duplicates(subset=["description", "category"]).copy()
    rows_after_exact_dedup = len(df_dedup)
    print(f"-> Remaining rows after exact duplicate removal: {rows_after_exact_dedup:,}")

    # 5. Check for conflicting labels: Same description with different categories
    print("\n[Audit] Inspecting conflicting descriptions (same description mapped to multiple categories)...")
    desc_label_counts = df_dedup.groupby("description")["category"].nunique()
    conflicting_descriptions = desc_label_counts[desc_label_counts > 1].index.tolist()
    num_conflicts = len(conflicting_descriptions)
    print(f"-> Unique descriptions with conflicting category labels: {num_conflicts}")

    if num_conflicts > 0:
        conflict_rows = df_dedup[df_dedup["description"].isin(conflicting_descriptions)].sort_values("description")
        print("\n   Conflicting Examples Detected:")
        for desc, group in conflict_rows.groupby("description"):
            cats = group["category"].tolist()
            print(f"   - '{desc}' -> Categories: {cats}")

        print("\n-> Conflict Resolution Strategy:")
        print("   To guarantee high-quality training labels and avoid training on contradictory data,")
        print(f"   dropping the {len(conflict_rows)} ambiguous rows ({num_conflicts} conflicting descriptions).")
        df_clean = df_dedup[~df_dedup["description"].isin(conflicting_descriptions)].copy()
    else:
        df_clean = df_dedup.copy()

    total_clean_rows = len(df_clean)
    print(f"-> Final unique, verified training rows: {total_clean_rows:,}")

    # 6. Feature Engineering: Normalized clean text for NLP modeling
    print("\n[Feature Engineering] Creating normalized NLP text feature...")
    df_clean["clean_text"] = df_clean["description"].apply(clean_text_for_nlp)
    # Ensure no empty clean_text
    df_clean = df_clean[df_clean["clean_text"] != ""].copy()

    # 7. Category distribution analysis
    print("\n[Distribution] Category breakdown after deduplication and cleaning:")
    print("-" * 50)
    print(f"{'Category':<20} {'Clean Rows':<12} {'% of Total':<10}")
    print("-" * 50)
    cat_counts = df_clean["category"].value_counts()
    for cat, count in cat_counts.items():
        pct = (count / len(df_clean)) * 100
        print(f"{cat:<20} {count:<12,} {pct:.2f}%")
    print("-" * 50)
    print(f"{'TOTAL':<20} {len(df_clean):<12,} 100.00%")
    print("-" * 50)

    # 8. Save cleaned dataset
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(sample_dir, exist_ok=True)

    out_clean_path = os.path.join(output_dir, "ai_training_clean.csv")
    df_clean[["description", "clean_text", "category"]].to_csv(out_clean_path, index=False)
    print(f"\n[Saved] Cleaned AI training dataset ({len(df_clean):,} rows): {out_clean_path}")

    # 9. Save sample demo dataset
    sample_df = df_clean.groupby("category").head(2).reset_index(drop=True)
    out_sample_path = os.path.join(sample_dir, "sample_ai_training.csv")
    sample_df[["description", "clean_text", "category"]].to_csv(out_sample_path, index=False)
    print(f"[Saved] Balanced sample dataset ({len(sample_df)} rows, 2 per category): {out_sample_path}")

    print("\n" + "=" * 75)
    print("DATASET B CLEANING COMPLETE - SUMMARY")
    print(f"Total raw rows:                     {total_raw_rows:,}")
    print(f"Exact duplicates removed:           {raw_duplicates:,}")
    print(f"Conflicting label rows removed:     {len(conflict_rows) if num_conflicts > 0 else 0}")
    print(f"Clean, unique training rows saved:  {len(df_clean):,}")
    print(f"Number of categories:               {df_clean['category'].nunique()} (All categories have >= {cat_counts.min():,} rows)")
    print("=" * 75)
    print("\nCRITICAL ML DATA HYGIENE RECOMMENDATIONS FOR PHASE 5:")
    print("1. Data Leakage Prevention:")
    print("   Split into train/test using StratifiedKFold or train_test_split (e.g. 80/20) on unique descriptions.")
    print("   Since duplicates were already purged, no identical descriptions can leak across train and test sets.")
    print("2. Domain Adaptation Note:")
    print("   Dataset B is US-banking oriented. For Indian expense tracking (UPI, Paytm, Swiggy, Zomato, etc.),")
    print("   we recommend a hybrid approach in Phase 5: combining this model with keyword matching and Indian sample priors.")
    print("=" * 75)

    return df_clean


if __name__ == "__main__":
    clean_dataset_b()
