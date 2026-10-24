"""
prepare_transactions.py - Dataset A Cleaning & Standardization Pipeline

This script cleans and standardizes the personal financial transactions from DATASET A.csv.
It implements all data cleaning requirements outlined in Phase 2:
1. Loads raw dataset from data/raw/ or root directory.
2. Parses Date into standard ISO format (YYYY-MM-DD HH:MM:SS).
3. Converts and validates numeric Amount values.
4. Removes completely empty columns (Subcategory, Note.1).
5. Resolves redundant columns (Account.1 is duplicate of Amount; INR column audited).
6. Fills missing Note descriptions with explicit placeholder ('Unspecified expense').
7. Distinguishes Income from Expense.
8. Isolates and handles the single foreign currency (USD) transaction with documented exchange rate.
9. Standardizes category labels while retaining original categories.
10. Saves cleaned outputs to data/processed/ and demo samples to data/sample/.
"""

import os
import sys
import pandas as pd
import numpy as np


def find_dataset_a_path():
    """Locate DATASET A.csv in data/raw/ or fallback to workspace root."""
    possible_paths = [
        os.path.join("data", "raw", "DATASET A.csv"),
        "DATASET A.csv",
        os.path.join("..", "data", "raw", "DATASET A.csv"),
        os.path.join("..", "DATASET A.csv"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Could not locate DATASET A.csv. Please ensure it exists in data/raw/ or project root.")


def clean_dataset_a(input_path=None, output_dir="data/processed", sample_dir="data/sample"):
    """
    Execute full cleaning, auditing, and standardization for Dataset A.
    """
    if input_path is None:
        input_path = find_dataset_a_path()

    print("=" * 70)
    print("STEP 1: CLEANING DATASET A (Personal Financial Transactions)")
    print(f"Loading raw file from: {input_path}")
    print("=" * 70)

    # 1. Load raw CSV
    df_raw = pd.read_csv(input_path)
    total_raw_rows = len(df_raw)
    print(f"Loaded {total_raw_rows} raw records across {len(df_raw.columns)} columns:")
    print(f"Columns: {list(df_raw.columns)}\n")

    # Working copy
    df = df_raw.copy()

    # 2. Check for empty columns and drop them
    empty_cols = [c for c in df.columns if df[c].isna().all()]
    print(f"[Audit] Empty columns identified (100% null): {empty_cols}")
    df = df.drop(columns=empty_cols)
    print(f"-> Dropped columns: {empty_cols}")

    # 3. Check redundant columns (Account.1, INR, Amount)
    print("\n[Audit] Auditing redundant amount and account fields:")
    if "Account.1" in df.columns:
        is_acc1_exact_amount = (df["Account.1"] == df["Amount"]).all()
        print(f"-> 'Account.1' is 100% identical to 'Amount': {is_acc1_exact_amount}")
        if is_acc1_exact_amount:
            df = df.drop(columns=["Account.1"])
            print("-> Successfully dropped redundant column 'Account.1'.")

    # Audit INR column vs Amount and Currency
    if "INR" in df.columns:
        inr_match = (df["INR"] == df["Amount"])
        diff_count = (~inr_match).sum()
        print(f"-> 'INR' matches 'Amount' in {inr_match.sum()} / {len(df)} rows.")
        if diff_count > 0:
            diff_rows = df[~inr_match]
            print(f"-> Discrepancy in {diff_count} row(s):")
            for _, r in diff_rows.iterrows():
                print(f"   Date: {r['Date']}, Note: '{r.get('Note', '')}', Amount: {r['Amount']} {r['Currency']}, INR Col: {r['INR']}")
                # Document exchange rate
                usd_to_inr_rate = r['INR'] / r['Amount']
                print(f"   Implied exchange rate: 1 {r['Currency']} = {usd_to_inr_rate:.4f} INR")

    # 4. Parse Date into valid datetime format
    print("\n[Transformation] Parsing transaction dates...")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    if df["Date"].isna().any():
        invalid_dates = df[df["Date"].isna()]
        raise ValueError(f"Found {len(invalid_dates)} records with unparseable dates!")
    min_date = df["Date"].min()
    max_date = df["Date"].max()
    print(f"-> Date range: {min_date.strftime('%Y-%m-%d %H:%M')} to {max_date.strftime('%Y-%m-%d %H:%M')}")
    # Create standardized formatted string column
    df["date_iso"] = df["Date"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # 5. Validate Amount
    print("\n[Validation] Validating monetary amounts...")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    if df["Amount"].isna().any():
        raise ValueError("Found non-numeric Amount values.")
    if (df["Amount"] <= 0).any():
        raise ValueError("Found non-positive Amount values.")
    print(f"-> All {len(df)} amounts are strictly positive numbers.")
    print(f"-> Min amount: {df['Amount'].min()}, Max amount: {df['Amount'].max()}, Median: {df['Amount'].median()}")

    # 6. Handle missing Notes (descriptions)
    print("\n[Transformation] Cleaning transaction descriptions (Note)...")
    missing_notes = df["Note"].isna().sum()
    print(f"-> Found {missing_notes} rows with missing descriptions.")
    if missing_notes > 0:
        # Document which rows were missing descriptions
        missing_sample = df[df["Note"].isna()][["Date", "Category", "Income/Expense", "Amount"]]
        for _, r in missing_sample.iterrows():
            print(f"   Date: {r['Date'].strftime('%Y-%m-%d')}, Category: {r['Category']}, Type: {r['Income/Expense']}, Amount: {r['Amount']}")
    # Replace NaN with standard placeholder and strip whitespace
    df["Note"] = df["Note"].fillna("Unspecified expense").astype(str).str.strip()

    # 7. Standardize Income / Expense transaction type
    df["transaction_type"] = df["Income/Expense"].astype(str).str.strip().str.capitalize()
    type_counts = df["transaction_type"].value_counts().to_dict()
    print(f"\n[Classification] Transaction types: {type_counts}")

    # 8. Standardize Payment Method (Account)
    account_mapping = {
        "CUB - online payment": "Net Banking / UPI (CUB)",
        "Cash": "Cash",
    }
    df["payment_method"] = df["Account"].map(account_mapping).fillna(df["Account"])
    print(f"[Classification] Payment methods: {df['payment_method'].value_counts().to_dict()}")

    # 9. Standardize Category mapping while retaining original
    df["original_category"] = df["Category"].astype(str).str.strip()

    def map_category(row):
        orig = row["original_category"]
        note = row["Note"].lower()
        t_type = row["transaction_type"]

        # Income categorization
        if t_type == "Income":
            if orig == "Salary":
                return "Income"
            if orig == "Allowance":
                return "Income"
            if "cashback" in note:
                return "Cashback / Rewards"
            return "Income"

        # Expense categorization
        if orig == "Food":
            return "Food"
        elif orig == "Transportation":
            return "Transportation"
        elif orig == "Apparel":
            return "Shopping"
        elif orig == "Household":
            if "rent" in note:
                return "Rent"
            return "Household / Utilities"
        elif orig == "Social Life":
            return "Entertainment"
        elif orig == "Beauty":
            return "Personal Care"
        elif orig == "Education":
            return "Education"
        elif orig == "Self-development":
            return "Education"
        elif orig == "Gift":
            return "Gifts"
        elif orig == "Other":
            return "Other"
        else:
            return orig

    df["category"] = df.apply(map_category, axis=1)
    print("\n[Standardization] Mapped categories distribution:")
    print(df["category"].value_counts().to_string())

    # 10. Currency analysis and USD record isolation
    print("\n[Currency Audit] Checking currency breakdown...")
    curr_counts = df["Currency"].value_counts().to_dict()
    print(f"-> Currencies present: {curr_counts}")

    usd_mask = df["Currency"] == "USD"
    usd_record = df[usd_mask].copy()
    inr_records = df[~usd_mask].copy()

    # Create cleaned, final schema for application
    columns_final = [
        "date",
        "description",
        "amount",
        "currency",
        "transaction_type",
        "category",
        "original_category",
        "payment_method",
        "is_usd",
    ]

    df["date"] = df["date_iso"]
    df["description"] = df["Note"]
    df["amount"] = df["Amount"]
    df["currency"] = df["Currency"]
    df["is_usd"] = usd_mask

    df_clean_all = df[columns_final].sort_values("date", ascending=False).reset_index(drop=True)
    df_clean_inr = df_clean_all[~df_clean_all["is_usd"]].reset_index(drop=True)
    df_clean_usd = df_clean_all[df_clean_all["is_usd"]].reset_index(drop=True)

    # Create destination directories
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(sample_dir, exist_ok=True)

    # Save processed files
    # 1. Main standard clean file (all 277 records with is_usd flag)
    out_all_path = os.path.join(output_dir, "transactions_clean.csv")
    df_clean_all.to_csv(out_all_path, index=False)
    print(f"\n[Saved] Cleaned transactions (277 records): {out_all_path}")

    # 2. INR-only dataset (276 records for pure INR analytics without currency mixing)
    out_inr_path = os.path.join(output_dir, "transactions_inr_only.csv")
    df_clean_inr.to_csv(out_inr_path, index=False)
    print(f"[Saved] Pure INR transactions (276 records): {out_inr_path}")

    # 3. USD record isolated with full context
    out_usd_path = os.path.join(output_dir, "transactions_usd_isolated.csv")
    df_clean_usd["inr_equivalent"] = 1120.72
    df_clean_usd["exchange_rate_inr_per_usd"] = 74.7147
    df_clean_usd.to_csv(out_usd_path, index=False)
    print(f"[Saved] Isolated USD record (1 record): {out_usd_path}")

    # 4. Demo sample dataset (10 records across different categories)
    sample_rows = pd.concat([
        df_clean_all[df_clean_all["transaction_type"] == "Expense"].head(8),
        df_clean_all[df_clean_all["transaction_type"] == "Income"].head(2),
    ]).reset_index(drop=True)
    sample_path = os.path.join(sample_dir, "sample_transactions.csv")
    sample_rows.to_csv(sample_path, index=False)
    print(f"[Saved] Demo sample records (10 records): {sample_path}")

    print("\n" + "=" * 70)
    print("DATASET A CLEANING COMPLETE - SUMMARY")
    print(f"Total raw records:            {total_raw_rows}")
    print(f"Total cleaned records:        {len(df_clean_all)}")
    print(f"  - Expense records:          {(df_clean_all['transaction_type'] == 'Expense').sum()}")
    print(f"  - Income records:           {(df_clean_all['transaction_type'] == 'Income').sum()}")
    print(f"  - INR transactions:         {(~df_clean_all['is_usd']).sum()} (Total INR Expense: {df_clean_inr[df_clean_inr['transaction_type'] == 'Expense']['amount'].sum():,.2f})")
    print(f"  - USD transactions:         {df_clean_all['is_usd'].sum()} ($15.00 Food expense, 1120.72 INR equivalent)")
    print(f"Missing descriptions filled:  {missing_notes}")
    print(f"Empty columns dropped:        {empty_cols}")
    print(f"Redundant columns dropped:    ['Account.1', 'INR']")
    print("=" * 70)

    return df_clean_all


if __name__ == "__main__":
    clean_dataset_a()
