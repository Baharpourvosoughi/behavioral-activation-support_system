# src/recommender.py

from rich.console import Console
from rich.table import Table
import os
import joblib
from collections import defaultdict

from src.db import (
    get_default_user_id, get_latest_log, get_all_tasks,
    get_recently_completed_task_ids, insert_recommendation,
    insert_task_history, get_connection
)

console = Console()

MODEL_PATH = os.path.join("models", "completion_predictor.joblib")

model = None
if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
    except:
        model = None


def predict_completion_probability(log, task):
    if model is None:
        return None

    mood, energy, stress, sleep, social, exercise = log
    task_id, name, category, difficulty, energy_required, social_level = task

    features = [[mood, energy, stress, difficulty, energy_required, social_level]]
    prob = model.predict_proba(features)[0][1]
    return prob


def get_user_category_preferences(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT t.category, COUNT(*)
        FROM task_history h
        JOIN tasks t ON h.task_id = t.task_id
        WHERE h.user_id = ? AND h.completed = 1
        GROUP BY t.category
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()

    prefs = defaultdict(int)
    for category, count in rows:
        prefs[category] = count

    return prefs


def score_task(task, log, recent_ids):
    task_id, name, category, difficulty, energy_required, social_level = task
    mood, energy, stress, sleep, social, exercise = log

    if task_id in recent_ids:
        return None

    score = 0
    reasons = []

    if energy <= 4:
        if energy_required == 1:
            score += 3
            reasons.append("matches your energy level today")
        elif energy_required == 3:
            score -= 2

    if stress >= 7:
        if category in ("mental", "selfcare"):
            score += 3
            reasons.append("can help when you're feeling stressed")

    if social <= 2:
        if social_level >= 2:
            score += 2
            reasons.append("good for days when you haven't talked to many people")

    if exercise < 15:
        if category == "movement":
            score += 2
            reasons.append("you haven't moved much today")

    if mood <= 4:
        if difficulty == 1:
            score += 2
            reasons.append("easy to start when you're not feeling great")

    score += 1

    reason_text = reasons[0] if reasons else "a solid option for today"
    return (score, task, reason_text)


def recommend():
    user_id = get_default_user_id()
    log = get_latest_log(user_id)

    if not log:
        console.print("[yellow]No log found yet. Log today's data first (option 1).[/yellow]")
        return

    tasks = get_all_tasks()
    recent_ids = get_recently_completed_task_ids(user_id)

    category_prefs = get_user_category_preferences(user_id)

    scored = []

    for t in tasks:
        result = score_task(t, log, recent_ids)

        if result is None:
            continue

        rule_score, task, reason = result
        task_id, name, category, *_ = task

        prob = predict_completion_probability(log, task)
        if prob is not None:
            rule_score += prob * 3

        if category in category_prefs:
            rule_score += category_prefs[category] * 0.5

        scored.append((rule_score, task, reason, prob))

    scored.sort(key=lambda x: x[0], reverse=True)

    top3 = scored[:3]

    if not top3:
        console.print("[yellow]Not enough tasks to suggest right now.[/yellow]")
        return

    table = Table(title="Suggested tasks for today", border_style="green")
    table.add_column("#", style="dim", width=3)
    table.add_column("Task", style="bold")
    table.add_column("Category", style="cyan")
    table.add_column("Why", style="dim")
    table.add_column("Completion %", style="magenta")

    for i, (score, task, reason, prob) in enumerate(top3, 1):
        task_id, name, category, *_ = task
        prob_text = f"{prob:.2f}" if prob is not None else "-"
        table.add_row(str(i), name, category, reason, prob_text)
        insert_recommendation(user_id, task_id, reason)

    console.print(table)

    console.print("\nDid you complete any of these? Enter 1, 2, or 3 — or press Enter to skip.")
    choice = console.input("[bold yellow]Your choice:[/bold yellow] ").strip()

    if choice in ("1", "2", "3"):
        idx = int(choice) - 1
        _, task, _, _ = top3[idx]
        insert_task_history(user_id, task[0], completed=1)
        console.print(f"[green]Nice, marked as done: {task[1]}[/green]")
    else:
        console.print("[dim]No problem. You can log completions next time.[/dim]")
