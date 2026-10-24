# Expense Tracker AI

An intelligent personal finance and expense tracking application featuring automated transaction categorization, interactive dashboards, budgeting alerts, and exportable financial reports.

---

## Project Architecture & Directory Structure

```text
expense-tracker-ai/
├── data/
│   ├── raw/                        # Original raw CSV files (DATASET A.csv, DATASET B.csv)
│   ├── processed/                  # Cleaned, audited, and standardized datasets
│   │   ├── transactions_clean.csv      # 277 cleaned records with ISO dates and mapped categories
│   │   ├── transactions_inr_only.csv   # 276 pure INR transactions for financial aggregations
│   │   ├── transactions_usd_isolated.csv # Single 15 USD record with documented historical rate (74.7147 INR/USD)
│   │   └── ai_training_clean.csv       # 45,692 unique, verified bank descriptions across 17 classes
│   └── sample/                     # Small, non-sensitive demo records
│       ├── sample_transactions.csv     # 10 representative transaction records
│       └── sample_ai_training.csv      # Balanced 34-row sample (2 per ML category)
│
├── data_processing/
│   └── prepare_transactions.py     # Dataset A cleaning & standardization pipeline
│
├── ai/
│   ├── prepare_training_data.py    # Dataset B cleaning, deduplication, conflict audit & NLP normalization
│   ├── train_model.py              # TF-IDF + Logistic Regression training (Phase 5)
│   ├── predict_category.py         # Category inference module (Phase 5)
│   └── models/                     # Serialized model artifacts (.joblib)
│
├── pages/                          # Streamlit multi-page application (Phase 4, 6, 7, 8)
│   ├── 1_Expenses.py               # Add, edit, delete, and AI-categorize transactions
│   ├── 2_Category_Analysis.py      # Category-wise expenditure breakdown
│   ├── 3_Dashboard.py              # Plotly interactive graphs, spending trends, and metrics
│   └── 4_Budget_Reports.py         # Monthly limits, alerts, and CSV/Excel exports
│
├── tests/                          # Automated unit test suite (Phase 9)
│   ├── test_database.py
│   ├── test_expenses.py
│   └── test_ai.py
│
├── app.py                          # Streamlit application home page
├── database.py                     # SQLite database setup and schema management (Phase 3)
├── expense_functions.py            # CRUD operations for transactions
├── analytics.py                    # Analytics aggregations and chart generation
├── budget_functions.py             # Monthly budgets and threshold alerting
├── report_functions.py             # CSV and Excel export utilities
├── requirements.txt                # Project dependencies
├── .gitignore                      # Git ignore patterns
└── README.md                       # Comprehensive documentation
```

---

## Dataset Analysis & Cleaning Summary

### 1. Dataset A: Personal Expense Transactions (`DATASET A.csv`)
- **Role:** Application testing, SQLite initial seed, financial analytics, and visual charts.
- **Raw Dimensions:** 277 records, 11 columns.
- **Date Coverage:** November 21, 2021 – March 2, 2022.
- **Auditing Findings:**
  - `Subcategory` and `Note.1` were 100% empty (dropped).
  - `Account.1` was an exact duplicate of `Amount` across all 277 rows (dropped).
  - `INR` column matched `Amount` for 276 rows, except row 217 (15.0 USD Food expense at Cash with 1120.72 INR equivalent; implied exchange rate: 74.7147 INR/USD).
  - 4 records lacked descriptions (`Note`). They were filled with `"Unspecified expense"` rather than fabricating entries.
  - 231 Expense records (Total INR: ₹57,903.28) and 46 Income records.
- **Currency Isolation:**
  - Saved `transactions_clean.csv` (all 277 records with `is_usd` boolean flag).
  - Saved `transactions_inr_only.csv` (276 INR records) to prevent unadjusted currency mixing in aggregate sums.
  - Preserved `transactions_usd_isolated.csv` containing the isolated $15.00 transaction.

### 2. Dataset B: Labeled Bank Descriptions (`DATASET B.csv`)
- **Role:** Machine-learning classifier training for AI transaction category suggestion.
- **Raw Dimensions:** 68,000 rows across 17 categories (exactly 4,000 rows per category).
- **Auditing Findings:**
  - **Duplicates:** Exactly **22,298** rows (32.79%) were exact duplicates and were removed.
  - **Label Conflicts:** 5 descriptions had contradictory category labels (e.g., `BATH & BODY WORKS` labeled as both `Shopping` and `Personal Care`; `RITE AID` labeled as both `Shopping` and `Healthcare`). These 10 ambiguous rows were dropped to guarantee unambiguous ground truth.
  - **Remaining Clean Data:** **45,692** unique, verified training rows.
  - **Class Distribution:** Every single category retains between 1,349 (Fees) and 3,962 (Shopping) unique examples.
  - **NLP Feature:** Created `clean_text` column stripping `[debit]`/`[credit]` prefixes and banking codes (`PPD ID: ...`), normalizing text for natural language input.

---

## Category Mapping Matrix

| Dataset A Raw Category | Standardized Application Category | Rationale / Mapping Rules |
| :--- | :--- | :--- |
| **Food** | `Food` | Daily dining, snacks, lunch, dinner |
| **Transportation** | `Transportation` | Metro, auto, bus fares |
| **Apparel** | `Shopping` | Clothes, hoodies, earphones |
| **Household** | `Rent` or `Household / Utilities` | Mapped to `Rent` if description mentions rent; otherwise household goods |
| **Social Life** | `Entertainment` | Outings and social gatherings |
| **Education** | `Education` | Exam/reval fees, academic expenses |
| **Self-development** | `Education` | Books and learning material |
| **Beauty** | `Personal Care` | Toiletries, grooming |
| **Gift** | `Gifts` | Birthday gifts and celebration spending |
| **Salary** | `Income` | Primary monthly income |
| **Allowance** | `Income` | Family transfers ("From dad") |
| **Petty cash** | `Cashback / Rewards` | Cashback refunds (e.g. ₹3 cashback) |
| **Other** | `Other` or `Income` | Classified as `Income` if `transaction_type == Income`, else `Other` |

---

## How to Run the Data Pipelines

### 1. Clean Dataset A
```bash
python data_processing/prepare_transactions.py
```
Outputs generated in `data/processed/`:
- `transactions_clean.csv` (277 records)
- `transactions_inr_only.csv` (276 records)
- `transactions_usd_isolated.csv` (1 record)
- `data/sample/sample_transactions.csv` (10 demo records)

### 2. Clean & Deduplicate Dataset B
```bash
python ai/prepare_training_data.py
```
Outputs generated:
- `data/processed/ai_training_clean.csv` (45,692 records)
- `data/sample/sample_ai_training.csv` (34 balanced demo records)

---

## How to Run the Application & Test Suite

### 1. Launch the Streamlit Web Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.
- Explore **1_Expenses** to record transactions with live AI categorization.
- Visit **2_Category_Analysis** for donut charts, spending distributions, and category trends.
- View **3_Dashboard** for interactive KPIs, trend lines, and budget utilization gauges.
- Navigate to **4_Budget_Reports** to set limits, receive alert warnings, and download CSV/Excel statements.

### 2. Run the Automated Pytest Suite
```bash
python -m pytest tests -v
```
All 15 automated unit tests verify:
- Database schema, table constraints, and connection pooling.
- CRUD operations and input validation (rejecting negative amounts and empty descriptions).
- AI model accuracy and Indian domain prior fallbacks.
- Financial analytics and income-exclusion invariants.
- Budget threshold alerts (`Normal`, `Warning` at 80%+, `Exceeded` at 100%+).

### 3. Machine Learning Model Performance
- **Algorithm:** TF-IDF Vectorizer (unigrams + bigrams) + Multinomial Logistic Regression (`L2`).
- **Accuracy:** `99.60%` on held-out 20% test set (9,139 records).
- **Macro F1-Score:** `99.63%`.
- **Model Path:** [ai/models/expense_category_model.joblib](file:///d:/Min-Gopi_proj/ai/models/expense_category_model.joblib).
- **Domain Adaptation:** Hybrid inference via [ai/predict_category.py](file:///d:/Min-Gopi_proj/ai/predict_category.py) ensures seamless handling of Indian payment descriptions (UPI, Swiggy, Zomato, Metro, Auto, Rent).
#
