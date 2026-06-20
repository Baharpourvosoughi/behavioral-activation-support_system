# experiments/seed_demo_data.py
"""
Seed synthetic demo data for the Behavioral Activation System.

This script creates artificial daily logs and task history entries so the
experimental ML models can be tested without waiting for weeks of real data.

Important:
- This data is synthetic/demo data.
- It should not be treated as real clinical or behavioral data.
"""

import os
import random
import sqlite3
from datetime import date, timedelta


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "app.db")

N_DAYS = 30
USER_ID = 1
RANDOM_SEED = 42

random.seed(RANDOM_SEED)


def get_connection():
    return sqlite3.connect(DB_PATH)


def table_columns(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]


def insert_dynamic(conn, table_name, data):
    """
    Inserts only the columns that actually exist in the target table.
    This makes the script more tolerant of small schema differences.
    """
    columns = table_columns(conn, table_name)

    filtered_data = {
        key: value
        for key, value in data.items()
        if key in columns
    }

    if not filtered_data:
        raise ValueError(f"No matching columns found for table: {table_name}")

    col_names = ", ".join(filtered_data.keys())
    placeholders = ", ".join(["?"] * len(filtered_data))
    values = list(filtered_data.values())

    query = f"""
        INSERT INTO {table_name} ({col_names})
        VALUES ({placeholders})
    """

    conn.execute(query, values)


def get_tasks(conn):
    cursor = conn.cursor()

    task_cols = table_columns(conn, "tasks")

    if "task_id" not in task_cols:
        raise ValueError("Expected column 'task_id' in tasks table.")

    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()

    tasks = []

    for row in rows:
        task = dict(zip(task_cols, row))
        tasks.append(task)

    return tasks


def clear_existing_demo_range(conn, start_date, end_date):
    """
    Removes existing rows in the demo date range to avoid duplicates
    if the script is run multiple times.
    """
    daily_cols = table_columns(conn, "daily_logs")
    history_cols = table_columns(conn, "task_history")

    if "log_date" in daily_cols:
        conn.execute(
            "DELETE FROM daily_logs WHERE log_date BETWEEN ? AND ?",
            (start_date, end_date)
        )

    if "task_date" in history_cols:
        conn.execute(
            "DELETE FROM task_history WHERE task_date BETWEEN ? AND ?",
            (start_date, end_date)
        )


def generate_daily_values(day_index):
    """
    Generates somewhat realistic synthetic behavioral patterns.

    The values are intentionally correlated:
    - More sleep and exercise usually improve mood/energy.
    - Higher stress usually lowers mood/energy.
    """

    # Weekly rhythm effect
    weekly_wave = 1.0 if day_index % 7 in [5, 6] else 0.0

    sleep_hours = round(random.uniform(5.0, 9.0), 1)
    exercise_minutes = random.choice([0, 5, 10, 15, 20, 30, 40, 45, 60])
    stress = random.randint(2, 9)

    mood_score = (
        4.5
        + 0.45 * (sleep_hours - 6.5)
        + 0.025 * exercise_minutes
        - 0.35 * (stress - 5)
        + weekly_wave
        + random.uniform(-1.0, 1.0)
    )

    energy_score = (
        4.5
        + 0.5 * (sleep_hours - 6.5)
        + 0.02 * exercise_minutes
        - 0.25 * (stress - 5)
        + random.uniform(-1.0, 1.0)
    )

    mood = max(1, min(10, round(mood_score)))
    energy = max(1, min(10, round(energy_score)))
    stress = max(1, min(10, stress))

    social_interaction = random.randint(1, 5)
    tasks_done = random.randint(0, 5)

    return {
        "mood": mood,
        "energy": energy,
        "stress": stress,
        "sleep_hours": sleep_hours,
        "social_interaction": social_interaction,
        "exercise_minutes": exercise_minutes,
        "tasks_done": tasks_done,
    }


def completion_probability(log_values, task):
    """
    Creates a simple synthetic probability of completing a task.

    Easier tasks and tasks requiring less energy become more likely
    when the user has low energy.
    """

    mood = log_values["mood"]
    energy = log_values["energy"]
    stress = log_values["stress"]

    difficulty = task.get("difficulty", 3) or 3
    energy_required = task.get("energy_required", 3) or 3
    social_level = task.get("social_level", 2) or 2

    probability = (
        0.55
        + 0.04 * (mood - 5)
        + 0.05 * (energy - 5)
        - 0.04 * (stress - 5)
        - 0.06 * (difficulty - 3)
        - 0.05 * (energy_required - 3)
        - 0.02 * (social_level - 2)
    )

    probability = max(0.1, min(0.9, probability))

    return probability


def seed_demo_data():
    conn = get_connection()

    try:
        tasks = get_tasks(conn)

        if not tasks:
            print("No tasks found in database.")
            print("Run the main app once first so default tasks are created.")
            return

        today = date.today()
        start = today - timedelta(days=N_DAYS - 1)
        end = today

        start_str = start.isoformat()
        end_str = end.isoformat()

        clear_existing_demo_range(conn, start_str, end_str)

        daily_count = 0
        history_count = 0

        for i in range(N_DAYS):
            current_date = start + timedelta(days=i)
            current_date_str = current_date.isoformat()

            log_values = generate_daily_values(i)

            daily_log_data = {
                "user_id": USER_ID,
                "log_date": current_date_str,
                "mood": log_values["mood"],
                "energy": log_values["energy"],
                "stress": log_values["stress"],
                "sleep_hours": log_values["sleep_hours"],
                "social_interaction": log_values["social_interaction"],
                "exercise_minutes": log_values["exercise_minutes"],
                "tasks_done": log_values["tasks_done"],
            }

            insert_dynamic(conn, "daily_logs", daily_log_data)
            daily_count += 1

            # Add 1 or 2 task history entries per day
            n_tasks_today = random.choice([1, 1, 2])

            selected_tasks = random.sample(
                tasks,
                k=min(n_tasks_today, len(tasks))
            )

            for task in selected_tasks:
                prob = completion_probability(log_values, task)
                completed = 1 if random.random() < prob else 0

                task_history_data = {
                    "user_id": USER_ID,
                    "task_id": task["task_id"],
                    "task_date": current_date_str,
                    "completed": completed,
                }

                insert_dynamic(conn, "task_history", task_history_data)
                history_count += 1

        conn.commit()

        print("Demo data created successfully.")
        print(f"Daily logs inserted: {daily_count}")
        print(f"Task history entries inserted: {history_count}")
        print()
        print("Now run:")
        print("  python experiments/ml_models.py")

    finally:
        conn.close()


if __name__ == "__main__":
    print("=== Seeding Synthetic Demo Data ===")
    seed_demo_data()
