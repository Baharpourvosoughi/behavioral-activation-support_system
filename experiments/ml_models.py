# experiments/ml_models.py

import os
import sqlite3
import warnings
import numpy as np

warnings.filterwarnings("ignore")

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "app.db")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

try:
    import pandas as pd
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, accuracy_score
    import joblib
    _DEPS_OK = True
except ImportError:
    _DEPS_OK = False


def load_daily_logs():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM daily_logs ORDER BY log_date ASC", conn
    )
    conn.close()
    return df


def load_task_history():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        """SELECT th.*, t.difficulty, t.energy_required, t.social_level, t.category
           FROM task_history th
           JOIN tasks t ON th.task_id = t.task_id
           ORDER BY th.task_date ASC""",
        conn
    )
    conn.close()
    return df


def build_mood_features(df):
    df = df.copy()

    df["mood_lag1"] = df["mood"].shift(1)
    df["energy_lag1"] = df["energy"].shift(1)
    df["stress_lag1"] = df["stress"].shift(1)
    df["sleep_lag1"] = df["sleep_hours"].shift(1)
    df["exercise_lag1"] = df["exercise_minutes"].shift(1)

    df = df.dropna()

    feature_cols = [
        "mood_lag1",
        "energy_lag1",
        "stress_lag1",
        "sleep_lag1",
        "exercise_lag1",
    ]

    X = df[feature_cols].values
    y = df["mood"].values

    return X, y, feature_cols


def build_completion_features(logs_df, history_df):
    merged = history_df.merge(
        logs_df[["log_date", "mood", "energy", "stress"]],
        left_on="task_date",
        right_on="log_date",
        how="inner"
    )

    feature_cols = [
        "mood",
        "energy",
        "stress",
        "difficulty",
        "energy_required",
        "social_level",
    ]

    merged = merged.dropna(subset=feature_cols + ["completed"])

    X = merged[feature_cols].values
    y = merged["completed"].astype(int).values

    return X, y, feature_cols


def train_mood_predictor(min_samples=10):
    if not _DEPS_OK:
        print("Missing dependencies. Run: pip install pandas scikit-learn joblib")
        return

    logs = load_daily_logs()

    if len(logs) < min_samples:
        print(
            f"[mood model] Need at least {min_samples} log entries. "
            f"Currently have {len(logs)}. Skipping."
        )
        return

    X, y, features = build_mood_features(logs)

    if len(X) < 5:
        print("[mood model] Not enough samples after feature engineering. Skipping.")
        return

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)

    print(f"[mood model] MSE on test set: {mse:.3f}  (n_test={len(y_test)})")
    print("[mood model] Feature importances:")

    importances = dict(zip(features, model.feature_importances_))

    for feat, imp in sorted(importances.items(), key=lambda x: -x[1]):
        bar = "█" * int(imp * 30)
        print(f"  {feat:<20} {bar} {imp:.3f}")

    print("\n[mood model] Interpretation (exploratory):")
    print("Features with higher importance may have stronger influence on next‑day mood.")

    os.makedirs(MODELS_DIR, exist_ok=True)
    path = os.path.join(MODELS_DIR, "mood_predictor.joblib")
    joblib.dump(model, path)
    print(f"[mood model] Saved to {path}")


def train_completion_predictor(min_samples=10):
    if not _DEPS_OK:
        print("Missing dependencies. Run: pip install pandas scikit-learn joblib")
        return

    logs = load_daily_logs()
    history = load_task_history()

    if len(history) < min_samples:
        print(
            f"[completion model] Need at least {min_samples} task history entries. "
            f"Currently have {len(history)}. Skipping."
        )
        return

    X, y, features = build_completion_features(logs, history)

    if len(X) < 5:
        print("[completion model] Not enough matched samples. Skipping.")
        return

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    print(f"[completion model] Accuracy on test set: {acc:.3f}  (n_test={len(y_test)})")
    print("[completion model] Feature importances:")

    importances = dict(zip(features, model.feature_importances_))

    for feat, imp in sorted(importances.items(), key=lambda x: -x[1]):
        bar = "█" * int(imp * 30)
        print(f"  {feat:<20} {bar} {imp:.3f}")

    print("\nBehavior Insight Report")
    print("-----------------------")

    top_features = sorted(importances.items(), key=lambda x: -x[1])[:3]

    for f, _ in top_features:
        if f == "mood":
            print("- Mood appears to strongly influence task completion.")
        elif f == "energy":
            print("- Higher energy levels increase task completion likelihood.")
        elif f == "stress":
            print("- Higher stress may reduce the chance of completing tasks.")
        elif f == "difficulty":
            print("- Task difficulty affects the likelihood of completion.")
        elif f == "energy_required":
            print("- Tasks requiring more energy are less likely to be completed when energy is low.")
        elif f == "social_level":
            print("- Social demand may influence whether tasks get completed.")

    print("\n[completion model] Interpretation (exploratory):")
    print("Features with higher importance may influence whether a task gets completed.")

    os.makedirs(MODELS_DIR, exist_ok=True)
    path = os.path.join(MODELS_DIR, "completion_predictor.joblib")
    joblib.dump(model, path)
    print(f"[completion model] Saved to {path}")


if __name__ == "__main__":
    print("=== Experimental ML Module ===")
    print("\nTraining mood predictor...\n")
    train_mood_predictor()
    print("\nTraining completion predictor...\n")
    train_completion_predictor()
