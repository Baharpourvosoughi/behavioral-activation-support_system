# BASS: Behavioral Activation Support System

A context-aware behavioral activation prototype for task recommendation, mood tracking, and longitudinal self-monitoring.

---

## Overview

BASS is a research-oriented software prototype inspired by Behavioral Activation (BA), an approach that encourages manageable and meaningful activities to help address patterns of inactivity.

The project began as a personal tracking tool and evolved into a computational prototype for exploring how daily self-reported state can inform task recommendations.

BASS currently combines four components:

1. Daily behavioral logging for mood, energy, stress, sleep, social interaction, exercise, and completed-task counts.
2. Context-aware task recommendation using rule-based scoring, optional machine-learning predictions, and historical completion counts.
3. Recent-log analytics for summarizing self-reported data and displaying simple rule-based observations.
4. Experimental machine learning for mood prediction and task-completion classification.

The system is a command-line prototype, not a validated mental health intervention. Its purpose is to explore how behavioral information and task characteristics can be combined in a simple recommendation pipeline.

A central research question motivating the project is:

> How can a task recommendation system use a person's current self-reported state and previous activity history to suggest tasks that may be more realistic to complete?

---

## Motivation

Many task-management systems treat tasks as independent of the user's current condition. BASS explores a different approach: task recommendations can account for self-reported mood, energy, stress, social interaction, and recent activity.

Tasks are stored with attributes such as:

* difficulty,
* category,
* energy requirement,
* social demand.

These attributes are combined with the user's latest log and historical task-completion records to produce a ranked list of candidate tasks.

The project also includes experimental machine-learning models to investigate whether these behavioral records can support predictions of mood and task completion.

Because real longitudinal data may take time to collect, a separate script generates synthetic demonstration data for initial testing. Synthetic results are intended for software experimentation, not as evidence of real human behavior.

---

## Main Features

### 1. Daily Behavioral Logging

The command-line logger records:

* mood on a scale of 1–10,
* energy on a scale of 1–10,
* stress on a scale of 1–10,
* sleep duration in hours,
* social interaction on a scale of 1–5,
* physical activity in minutes,
* number of tasks completed.

Records are stored in a local SQLite database.

The current implementation allows multiple logs for the same user on the same date. The recommendation system retrieves a latest log by date, while the analytics module operates on the most recent records rather than enforcing one record per calendar day.

### 2. Context-Aware Task Recommendation

The recommender assigns each candidate task a rule-based score using the user's latest logged state and the task's attributes.

It can also add two optional sources of information:

* a predicted completion probability from a trained classifier, if the model artifact is available;
* a bonus based on the number of previously completed tasks in the same category.

Tasks completed recently are excluded from the candidate list. The remaining tasks are sorted by their final scores, and up to three recommendations are displayed.

The current implementation uses fixed heuristic adjustments rather than a normalized weighted formula. It does not apply a hard energy-based exclusion rule.

See [Recommendation Logic](#recommendation-logic) for details.

### 3. Recent-Log Analytics

The analytics module summarizes the most recent seven log records, when available.

It displays:

* recorded mood, energy, stress, and sleep values,
* averages across the retrieved records,
* a snapshot of the latest retrieved record,
* simple rule-based observations about recent mood changes, stress, sleep, and energy.

The module uses recorded entries rather than enforcing a complete set of seven distinct calendar days. Consequently, its averages may cover fewer than seven calendar days or include multiple records from the same day.

The observations are descriptive rules, not clinical assessments or validated predictions.

### 4. Experimental Predictive Modeling

The experimental module includes two models:

* a `RandomForestRegressor` for predicting mood from lagged behavioral features;
* a `RandomForestClassifier` for predicting whether a recorded task was completed.

The models are trained from records in the local SQLite database and saved as joblib artifacts.

The completion classifier can be used by the recommender when its saved artifact is available. The mood predictor is currently an experimental standalone model and is not integrated into the recommendation flow.

The models are exploratory and have not been clinically validated.

---

## Recommendation Logic

The recommendation system is implemented in `src/recommender.py`.

It combines a rule-based score with optional model predictions and historical category-completion counts.

### 1. Base score and contextual rules

Every eligible task starts with a base score of 1.

The score is then adjusted according to the user's latest logged state:

| Condition | Score adjustment |
|---|---|
| Energy is 4 or lower and the task's energy requirement is 1 | +3 |
| Energy is 4 or lower and the task's energy requirement is 3 | −2 |
| Stress is 7 or higher and the task category is mental or selfcare | +3 |
| Social interaction is 2 or lower and task social level is at least 2 | +2 |
| Exercise is below 15 minutes and the task category is movement | +2 |
| Mood is 4 or lower and task difficulty is 1 | +2 |

These rules use fixed thresholds and score adjustments. They do not calculate a separate normalized feasibility score.

For each task, the displayed explanation is the first applicable explanation in the rule-evaluation order. If no explanation applies, a default message is used.

### 2. Predicted completion probability

If `models/completion_predictor.joblib` exists and loads successfully, the recommender uses the classifier to estimate task-completion probability.

The model receives six features, in this order:

1. mood,
2. energy,
3. stress,
4. task difficulty,
5. task energy requirement,
6. task social level.

The probability returned for the positive class is multiplied by 3 and added to the rule-based score:

```
final_score = rule_score + 3 * completion_probability
```

If the model is unavailable or fails to load, this component is omitted.

The probability is displayed separately from the ranking score. The current terminal display formats the probability as a decimal between 0 and 1, or displays a dash when the model is unavailable.

### 3. Historical category-completion counts

The recommender queries `task_history` and counts completed tasks in each category for the current user.

For each previously completed task in a category, eligible tasks in that category receive an additional 0.5 points:

```
category_bonus = 0.5 * completed_task_count_in_category
```

This is a count-based preference signal, not a completion rate. It does not divide completed tasks by the number of attempts or recommendations in that category.

### 4. Candidate filtering and ranking

Tasks recorded as completed within the recent-completion window are excluded before ranking.

All remaining tasks are scored and sorted in descending order. The system displays up to three recommendations and stores the displayed recommendations in the database.

The user can select one of the displayed options to record it as completed. Skipping the prompt does not currently create an explicit incomplete task-history record for each displayed recommendation.

#### Current design limitations

The recommendation logic currently has:

* fixed rule thresholds and score adjustments,
* an optional classifier contribution,
* category bonuses based on completion counts,
* no independent normalized feasibility score,
* no hard energy-based exclusion filter,
* no adaptive online learning of scoring parameters.

The resulting score is a heuristic ranking value, not a calibrated probability of task suitability or a clinical measure.

---

## Machine Learning Pipeline

The experimental machine-learning pipeline is implemented in `experiments/ml_models.py`.

### A. Mood Prediction

A `RandomForestRegressor` predicts the mood value associated with the current record using five lagged features:

* previous record's mood,
* previous record's energy,
* previous record's stress,
* previous record's sleep duration,
* previous record's exercise duration.

The data are ordered by `log_date` before lag features are constructed. The lag therefore refers to the preceding record in the ordered dataset, which is not necessarily the previous calendar day.

Rows without the required lagged values are removed.

The model is evaluated using mean squared error (MSE). Feature importance values are also reported as a basic model diagnostic.

### B. Task-Completion Prediction

A `RandomForestClassifier` predicts the recorded completion label using:

* mood,
* energy,
* stress,
* task difficulty,
* task energy requirement,
* task social level.

Task-history records are joined with daily logs by matching `task_date` to `log_date`.

The model is evaluated using accuracy, and feature importance values are reported.

The current pipeline uses a random train/test split. It does not implement a time-based holdout or a dedicated per-user evaluation protocol.

### C. Model Artifacts

The module saves the trained models to:

* `models/mood_predictor.joblib`
* `models/completion_predictor.joblib`

The recommender loads the completion model from the second path when the artifact is available.

Model files are generated outputs and must be created by running the training pipeline before they can be used.

### D. Interpretation and Evaluation Limitations

Feature importance describes how a trained model uses features for prediction. It does not establish that a feature causes a particular outcome.

The current training and evaluation workflow is experimental. Its results may be affected by:

* small sample sizes,
* synthetic or non-representative records,
* random train/test splitting,
* class imbalance,
* repeated observations from the same user,
* and the limited set of input features.

The reported metrics should not be interpreted as evidence of clinical effectiveness or reliable real-world performance.

---

## Synthetic Demo Data

The script `experiments/seed_demo_data.py` creates synthetic daily logs and task-history records for initial testing.

By default, it generates 30 days of data using a fixed random seed.

The generated daily values include mood, energy, stress, sleep, social interaction, exercise, and task counts. The generator introduces predefined relationships between selected variables, such as lower mood and energy under higher stress.

Task-completion labels are sampled from a hand-designed probability formula that depends on the generated state and task attributes.

The synthetic dataset is intended to test the database and machine-learning workflow. It is not real behavioral data and cannot establish that the same relationships hold in people.

> **Important:** The current script deletes daily-log and task-history records within the generated date range before inserting new data. This deletion is based on dates rather than user ID. Back up the database before running the script against a database containing real data.

For safer experimentation, use a disposable database containing only demonstration data.

---

## Repository Structure

```
BASS/
│
├── main.py
│
├── src/
│   ├── db.py
│   ├── logger.py
│   ├── recommender.py
│   └── analytics.py
│
└── experiments/
    ├── ml_models.py
    └── seed_demo_data.py
```

| File | Responsibility |
|---|---|
| `main.py` | Entry point for the command-line application |
| `src/db.py` | SQLite schema initialization, default task seeding, and database helpers |
| `src/logger.py` | Interactive daily behavioral logging |
| `src/recommender.py` | Rule-based task ranking, optional completion prediction, and category-completion bonuses |
| `src/analytics.py` | Recent-log summaries and rule-based observations |
| `experiments/ml_models.py` | Experimental mood-regression and task-completion-classification pipeline |
| `experiments/seed_demo_data.py` | Synthetic data generation for experimentation |

---

## Requirements

The application uses Python and the following libraries:

* `rich` for terminal formatting and tables,
* `numpy` for numerical utilities in the experimental module,
* `pandas` for loading and preparing data,
* `scikit-learn` for the machine-learning models and evaluation metrics,
* `joblib` for saving and loading trained models.

SQLite is accessed through Python's standard-library `sqlite3` module.

Install the dependencies listed in `requirements.txt` before running the application or experimental pipeline.

---

## How to Run

### 1. Install dependencies

Create and activate a virtual environment if needed, then install the dependencies:

```bash
pip install -r requirements.txt
```

The actual contents of `requirements.txt` should be checked to ensure all required packages are listed.

### 2. Start the application

Run:

```bash
python main.py
```

The application initializes the database and presents a command-line menu with the following options:

1. Log today's data.
2. Get task suggestions.
3. View recent behavioral summaries.
4. Exit.

### 3. Generate demonstration data

If you want to test the experimental models without first collecting real data, use a disposable database and run:

```bash
python experiments/seed_demo_data.py
```

The script expects the database schema and task records to exist. Run the application once to initialize the database and seed the default tasks.

> **Caution:** The current demonstration script deletes daily-log and task-history records in its target date range. Do not run it against a database containing data you need to preserve.

### 4. Train the experimental models

Run:

```bash
python experiments/ml_models.py
```

The script attempts to train both the mood predictor and completion classifier, subject to their minimum-data checks.

The generated model files are stored in the `models/` directory.

---

## Research Relevance

BASS is related to several areas of research:

* human-centered AI,
* behavior-aware recommender systems,
* longitudinal self-tracking,
* context-aware recommendation,
* applied machine learning for personal-support tools.

The prototype explores whether a small set of self-reported behavioral signals and task attributes can be used to rank activities according to the user's recorded circumstances.

Its current implementation is best understood as an early-stage engineering and research prototype. It does not yet demonstrate that personalized recommendations improve task completion, that model predictions generalize to unseen users, or that the system provides a clinically effective intervention.

A rigorous evaluation would require a clearly defined research question, suitable real-world data collection, appropriate comparison baselines, and evaluation metrics aligned with the intended outcome.

---

## Limitations

1. **No clinical validation:** BASS is not a validated mental-health intervention or clinical decision system.
2. **Synthetic data:** Synthetic records are generated from hand-designed rules and may not represent real behavioral patterns.
3. **Heuristic recommendation:** The current scoring system uses fixed rules rather than learned or adaptively optimized ranking weights.
4. **Count-based preferences:** Category bonuses reflect the number of recorded completions, not completion rates or explicitly stated user preferences.
5. **Incomplete outcome logging:** Skipped recommendations are not automatically recorded as incomplete attempts.
6. **Preliminary evaluation:** The experimental models use a random train/test split and limited metrics.
7. **No per-user modeling protocol:** The current training functions load records across users rather than implementing a dedicated personalized training and evaluation pipeline.
8. **Repeated daily records:** Multiple logs per user per day are permitted, which can affect the interpretation of recent-record analytics and temporal features.
9. **CLI interface:** The project is a local command-line application, not a deployed production service.
10. **Data-management risks:** The synthetic-data script deletes records in its target date range without restricting deletion to a specific user.

---

## Future Work

Potential next steps include:

* protecting real records when generating demonstration data,
* defining a consistent daily-log policy,
* recording outcomes for all displayed recommendations,
* comparing heuristic recommendations with simple baselines,
* evaluating the completion model with metrics beyond accuracy,
* using time-aware evaluation for temporal prediction,
* separating user-level training and evaluation where appropriate,
* testing whether personalization improves recommendation quality,
* and gathering consented, appropriately protected real-world data before making behavioral claims.

More advanced approaches, such as contextual bandits, should be considered only after the project has a reliable outcome-logging strategy and a defensible evaluation protocol.

---

## Disclaimer

BASS is an experimental software project for research and learning purposes.

It is not a medical device, clinical decision system, or substitute for professional mental-health care. Its scores and predictions should not be used to diagnose a condition or determine treatment.

Synthetic data and exploratory model outputs must not be interpreted as clinical or behavioral evidence.

---

## Author

**Bahar Pourvosoughi**
Computer Science Undergraduate
Islamic Azad University, Central Tehran Branch
