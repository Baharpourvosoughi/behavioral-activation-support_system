# Behavioral Activation System

A CLI-based mental health tool that helps you track your daily state and get personalized task recommendations. Built on behavioral activation principles—the idea that doing meaningful activities improves mood and breaks the cycle of avoidance and low energy.

## What It Does

- Daily Check-ins: Log your mood, energy, stress, sleep quality, social interaction, and exercise
- Smart Recommendations: Get task suggestions based on your current state and past patterns
- Progress Tracking: See weekly trends in your metrics
- ML Predictions: Optional machine learning models predict mood patterns and task completion likelihood
- Task Categories: Activities organized by type (social, physical, creative, etc.)

## Task Categories

The system includes 24 seed tasks across these categories:

- Social: Call a friend, meet someone for coffee, join a group activity
- Physical: Walk outside, stretch, yoga session, gym workout
- Creative: Draw/paint, write in journal, play music, work on hobby project
- Productive: Organize workspace, complete small work task, plan the week, clean one room
- Self-care: Take a relaxing bath, cook a healthy meal, read for pleasure, listen to favorite music
- Learning: Watch educational video, read an article, practice a skill, explore new topic

## Project Structure

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
├── main.py                # Entry point
├── requirements.txt
└── README.md

## Database Schema

users
- user_id (primary key)
- name
- created_at

daily_logs
- log_id (primary key)
- user_id (foreign key)
- date
- mood (1-10)
- energy (1-10)
- stress (1-10)
- sleep_hours
- social_interaction (1-10)
- exercise_minutes
- notes

tasks
- task_id (primary key)
- title
- category
- baseline_effort (1-5)
- baseline_mood_lift (1-5)

recommendations
- rec_id (primary key)
- user_id (foreign key)
- date
- recommended_tasks (JSON array)

task_history
- history_id (primary key)
- user_id (foreign key)
- task_id (foreign key)
- completed_date
- actual_effort (1-5)
- actual_mood_lift (1-5)

## Setup and Installation

1. Clone or download the project

2. Set up a virtual environment (recommended)

python -m venv venv  
source venv/bin/activate  
Windows: venv\Scripts\activate  

3. Install dependencies

pip install rich pandas scikit-learn joblib

4. Run the application

python main.py

The database will be created automatically on first run with seed tasks already loaded.

5. Optional: Generate demo data and train ML models

python experiments/seed_demo_data.py  
python experiments/ml_models.py  

This creates mood_predictor.joblib and completion_predictor.joblib in the models directory.

## How to Use It

Daily Workflow

1. Run python main.py
2. Select Log Today's Data
3. Answer the prompts about your current state
4. Select Get Task Recommendations
5. Review suggestions and pick one
6. Complete the task
7. Log the actual effort and mood impact

Main Menu Options

1. Log Today's Data
2. Get Task Recommendations
3. View Weekly Analytics
4. Exit

Example Session

You log in feeling mood=4, energy=3, stress=7, poor sleep, minimal social contact.

The system recommends:
- Take a 10-minute walk outside
- Text a friend to check in
- Listen to your favorite music

You choose the walk and log:
Actual effort: 2/5  
Mood lift: +3

Next time you're in a similar state, walking tasks will receive a higher recommendation weight.

## Recommendation Algorithm

The system scores each task based on:

- Energy Match
- Historical Success
- Mood Lift Potential
- Category Preference
- ML Prediction (if models exist)

score = energy_match + historical_success + baseline_mood_lift + category_preference + ml_boost

Tasks are ranked and the top suggestions are shown.

## Machine Learning Models

Mood Predictor
- Input: recent daily metrics
- Output: predicted next-day mood
- Model: Random Forest Regressor

Completion Predictor
- Input: current state + task attributes
- Output: probability of task completion
- Model: Logistic Regression

Training

Models train on historical data. With demo data they learn from 90 days of synthetic logs. You can retrain them later with real data.

## Notes & Disclaimers

- ML models are optional
- Demo data is synthetic
- This tool is not a replacement for professional mental health care
- Data is stored locally in SQLite

## Future Improvements

- Mobile app version
- Richer ML features (time-of-day patterns, weather data, streaks)
- Social accountability features
- Guided relaxation or breathing exercises
- Integration with calendar and habit trackers

Made with care for mental health and productivity
