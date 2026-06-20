```markdown
# Behavioral Activation System

A CLI-based mental health tool that helps you track your daily state and get personalized task recommendations. Built on behavioral activation principles—the idea that doing meaningful activities improves mood and breaks the cycle of avoidance and low energy.

## What It Does

- **Daily Check-ins**: Log your mood, energy, stress, sleep quality, social interaction, and exercise
- **Smart Recommendations**: Get task suggestions based on your current state and past patterns
- **Progress Tracking**: See weekly trends in your metrics
- **ML Predictions**: Optional machine learning models predict mood patterns and task completion likelihood
- **Task Categories**: Activities organized by type (social, physical, creative, etc.)

## Task Categories

The system includes 24 seed tasks across these categories:

- **Social**: Call a friend, meet someone for coffee, join a group activity
- **Physical**: Walk outside, stretch, yoga session, gym workout
- **Creative**: Draw/paint, write in journal, play music, work on hobby project
- **Productive**: Organize workspace, complete small work task, plan the week, clean one room
- **Self-care**: Take a relaxing bath, cook a healthy meal, read for pleasure, listen to favorite music
- **Learning**: Watch educational video, read an article, practice a skill, explore new topic

```
## Project Structure

behavioral-activation-system/

├── src/

│ ├── db.py # Database setup and operations

│ ├── logger.py # Daily check-in interface

│ ├── recommender.py # Task recommendation engine

│ └── analytics.py # Weekly trends and insights

├── experiments/

│ ├── ml_models.py # ML model training scripts

│ └── seed_demo_data.py # Generate synthetic data for testing

├── data/

│ └── app.db # SQLite database (auto-created)

├── models/

│ ├── mood_predictor.joblib

│ └── completion_predictor.joblib

├── main.py # Entry point

├── requirements.txt

└── README.md
```

```
## Database Schema

**users**
- `user_id` (primary key)
- `name`
- `created_at`

**daily_logs**
- `log_id` (primary key)
- `user_id` (foreign key)
- `date`
- `mood` (1-10)
- `energy` (1-10)
- `stress` (1-10)
- `sleep_hours`
- `social_interaction` (1-10)
- `exercise_minutes`
- `notes`

**tasks**
- `task_id` (primary key)
- `title`
- `category`
- `baseline_effort` (1-5)
- `baseline_mood_lift` (1-5)

**recommendations**
- `rec_id` (primary key)
- `user_id` (foreign key)
- `date`
- `recommended_tasks` (JSON array)

**task_history**
- `history_id` (primary key)
- `user_id` (foreign key)
- `task_id` (foreign key)
- `completed_date`
- `actual_effort` (1-5)
- `actual_mood_lift` (1-5)

## Setup and Installation

1. **Clone or download the project**

2. **Set up a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install rich pandas scikit-learn joblib
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

   The database will be created automatically on first run with seed tasks already loaded.

5. **Optional: Generate demo data and train ML models**:
   ```bash
   # Generate 90 days of synthetic data
   python experiments/seed_demo_data.py
   
   # Train the models
   python experiments/ml_models.py
   ```

   This creates `mood_predictor.joblib` and `completion_predictor.joblib` in the `models/` directory.

## How to Use It

### Daily Workflow

1. Run `python main.py`
2. Select "Log Today's Data" from the menu
3. Answer the prompts about your current state
4. Select "Get Task Recommendations"
5. Review suggestions and pick what feels doable
6. Do the task
7. Come back and mark it complete with actual effort/mood impact

### Main Menu Options

1. **Log Today's Data**: Daily check-in to record your current state
2. **Get Task Recommendations**: See personalized task suggestions
3. **View Weekly Analytics**: Check trends in your mood, energy, stress, sleep, social interaction, and exercise
4. **Exit**: Close the application

### Example Session


You log in feeling mood=4, energy=3, stress=7, poor sleep, minimal social contact.

The system recommends:
- "Take a 10-minute walk outside" (low effort, proven mood boost)
- "Text a friend to check in" (social, matches your low energy)
- "Listen to your favorite music" (self-care, easy win)

You pick the walk. After completing it, you log:
- Actual effort: 2/5 (easier than expected)
- Mood lift: +3 (felt noticeably better)

The system learns from this. Next time you're in a similar state, walks get weighted higher.

## Recommendation Algorithm

The system scores each task based on:

1. **Energy Match**: Tasks with effort ratings close to your current energy get higher scores
2. **Historical Success**: Tasks you've completed before and rated positively get boosted
3. **Mood Lift Potential**: Tasks with higher baseline mood impact score better
4. **Category Preference**: Tracks which categories you tend to complete and prefer
5. **ML Prediction** (if models exist): Uses trained models to predict completion likelihood

**Scoring formula**:

score = energy_match_score + historical_success + baseline_mood_lift + category_preference + ml_boost

Tasks are ranked by score and the top recommendations are shown.

## Machine Learning Models

### Mood Predictor
- **Input**: Recent daily metrics (mood, energy, stress, sleep, social, exercise)
- **Output**: Predicted mood for next day
- **Purpose**: Identifies patterns in your data to forecast low-mood days
- **Model**: Random Forest Regressor

### Completion Predictor
- **Input**: Current state + task attributes (effort, category, baseline mood lift)
- **Output**: Probability you'll complete this task
- **Purpose**: Filters recommendations to show tasks you're likely to follow through on
- **Model**: Logistic Regression

### Training Process
Both models train on your historical data (if you run the optional ML training script). With demo data, they learn from 90 days of synthetic patterns. As you use the app and log real completions, you can retrain models on your actual patterns.

## Notes & Disclaimers

- The ML models are optional—the core recommendation system works without them
- Demo data is synthetic and for testing only
- This is a personal tool, not a replacement for professional mental health care
- The database is local SQLite—your data stays on your machine

## Future Improvements

- Mobile app version
- Richer ML features (time-of-day patterns, weather data, streaks)
- Social accountability features (share progress with a friend)
- Guided relaxation/breathing exercises built-in
- Integration with calendar and habit trackers

**Made with care for mental health and productivity**
