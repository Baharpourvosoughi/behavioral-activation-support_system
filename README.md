
# Behavioral Activation System

A CLI tool built on Behavioral Activation principles to help track your daily state and receive personalized activity recommendations.

---

## What It Does

- **Daily Check-ins** — Log mood, energy, stress, sleep quality, social interaction, and exercise
- **Smart Recommendations** — Get task suggestions based on your current state and past patterns
- **Progress Tracking** — View weekly trends across all metrics
- **ML Predictions** — Optional machine learning models to predict mood patterns and task completion likelihood
- **Task Categories** — Activities organized by type (social, physical, creative, and more)

---

## Task Categories

24 default tasks across 6 categories:

| Category | Examples |
|---|---|
| Social | Call a friend, Meet someone for coffee |
| Physical | 10-min walk, Stretching routine |
| Creative | Sketch something, Write freely for 5 min |
| Productive | Tidy one area, Plan tomorrow |
| Self-care | Take a proper break, Cook a real meal |
| Learning | Read 10 pages, Watch an educational video |

---

## Project Structure

    ```
    behavioral-activation-system/
    ├── src/
    │   ├── db.py              # Database setup and operations
    │   ├── logger.py          # Daily check-in interface
    │   ├── recommender.py     # Task recommendation engine
    │   └── analytics.py       # Weekly trends and insights
    ├── experiments/
    │   ├── ml_models.py       # ML model training scripts
    │   └── seed_demo_data.py  # Generate synthetic data for testing
    ├── data/
    │   └── app.db             # SQLite database (auto-created)
    ├── models/
    │   ├── mood_predictor.joblib
    │   └── completion_predictor.joblib
    ├── main.py
    ├── requirements.txt
    └── README.md
    ```

---

## Database Schema

**users** — user_id, name, created_at

**daily_logs** — log_id, user_id, date, mood (1-10), energy (1-10), stress (1-10), sleep_hours, social_interaction (1-10), exercise_minutes, notes

**tasks** — task_id, title, category, baseline_effort (1-5), baseline_mood_lift (1-5)

**recommendations** — rec_id, user_id, date, recommended_tasks (JSON array)

**task_history** — history_id, user_id, task_id, completed_date, actual_effort (1-5), actual_mood_lift (1-5)

---

## Setup and Installation

Clone the project:

    ```
    git clone https://github.com/your-username/behavioral-activation-system.git
    cd behavioral-activation-system
    ```

Set up a virtual environment:

    ```
    python -m venv venv
    source venv/bin/activate        # macOS/Linux
    venv\Scripts\activate           # Windows
    ```

Install dependencies:

    ```
    pip install rich pandas scikit-learn joblib
    ```

Run the app:

    ```
    python main.py
    ```

The database and default tasks are created automatically on first run.

**Optional — generate demo data and train ML models:**

    ```
    python experiments/seed_demo_data.py
    python experiments/ml_models.py
    ```

This creates mood_predictor.joblib and completion_predictor.joblib in the models/ folder.

---

## How to Use It

### Daily Workflow

1. Run python main.py
2. Select **Log Today's Data** and answer the prompts
3. Select **Get Task Recommendations**
4. Review suggestions and pick one
5. Complete the task
6. Log your actual effort and mood impact

### Main Menu Options

1. Log Today's Data
2. Get Task Recommendations
3. View Weekly Analytics
4. Exit

### Example Session

You open the app feeling low mood (4/10) and low energy (3/10). The system scores all tasks against your current state and past patterns, then surfaces three suggestions — a short walk, calling a friend, and a light creative activity. You choose the walk, complete it, and log that it took moderate effort but gave a noticeable mood lift. That feedback improves future recommendations for similar days.

---

## Recommendation Algorithm

Each task is scored across five factors:

- **Energy Match** — How well the task effort fits your current energy
- **Historical Success** — Your past completion and mood-lift rates for this task
- **Mood Lift Potential** — Baseline mood improvement score for this task type
- **Category Preference** — How often you engage with this category
- **ML Prediction** — Completion probability from the trained model (if available)

Score formula:

    score = energy_match + historical_success + baseline_mood_lift + category_preference + ml_boost

Tasks are ranked by score and the top results are shown.

---

## Machine Learning Models

**Mood Predictor**
- Input: recent daily metrics
- Output: next-day mood prediction
- Model: Random Forest Regressor

**Completion Predictor**
- Input: current state + task features
- Output: probability of completing the task
- Model: Logistic Regression

**Training**

Models train on your historical data. With demo data, they learn from 90 days of synthetic patterns. They can be retrained at any time as your real data grows.

---

## Notes and Disclaimers

- ML models are optional — the app works without them
- Demo data is synthetic and for testing only
- This tool is not a replacement for professional mental health care
- All data is stored locally in SQLite

---

## Future Improvements

- Mobile version
- Advanced ML features (time-of-day patterns, weather, streaks)
- Social accountability features
- Guided relaxation exercises
- Calendar and habit tracker integrations

---

*Made with care for mental health and productivity.*

