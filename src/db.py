# src/db.py

import sqlite3
import os
from datetime import date, datetime

DB_PATH = "data/app.db"

SEED_TASKS = [
    ("Go for a 10-minute walk outside", "movement", 1, 1, 1),
    ("Do a short stretching routine", "movement", 1, 1, 1),
    ("Ride your bike around the block", "movement", 2, 2, 1),
    ("Do 15 minutes of any exercise you like", "movement", 2, 2, 1),
    ("Take a proper shower and get dressed", "selfcare", 1, 1, 1),
    ("Make yourself a real meal", "selfcare", 1, 1, 1),
    ("Go to bed at a reasonable hour tonight", "selfcare", 1, 1, 1),
    ("Step outside for some fresh air", "selfcare", 1, 1, 1),
    ("Tidy up your desk or workspace", "environment", 1, 1, 1),
    ("Wash the dishes or clean up the kitchen", "environment", 1, 1, 1),
    ("Organize one small area of your room", "environment", 2, 2, 1),
    ("Write down 3 things that went okay today", "mental", 1, 1, 1),
    ("Read something you actually enjoy", "mental", 1, 1, 1),
    ("Spend 10 minutes away from screens", "mental", 1, 1, 1),
    ("Write freely for 5 minutes, no rules", "mental", 1, 1, 1),
    ("Text someone you haven't talked to recently", "social", 1, 1, 2),
    ("Call a friend or family member", "social", 2, 1, 3),
    ("Make small talk with someone today", "social", 1, 1, 2),
    ("Plan to meet someone this week", "social", 2, 2, 3),
    ("Open your project and do just one small thing", "project", 1, 2, 1),
    ("Review your notes from last time", "project", 1, 1, 1),
    ("Write a few lines of code or notes", "project", 2, 2, 1),
    ("Look up one thing you've been stuck on", "project", 2, 2, 1),
    ("Outline what you want to do next session", "project", 1, 1, 1),
]


def get_connection():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start_date TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            log_date TEXT NOT NULL,
            mood INTEGER,
            energy INTEGER,
            stress INTEGER,
            sleep_hours REAL,
            social_interaction INTEGER,
            exercise_minutes INTEGER,
            tasks_done INTEGER
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            difficulty INTEGER,
            energy_required INTEGER,
            social_level INTEGER
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task_id INTEGER,
            rec_date TEXT,
            reason TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS task_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task_id INTEGER,
            task_date TEXT,
            completed INTEGER DEFAULT 0,
            completed_at TEXT
        )
    """)

    c.execute("SELECT COUNT(*) FROM tasks")
    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO tasks (name, category, difficulty, energy_required, social_level) VALUES (?, ?, ?, ?, ?)",
            SEED_TASKS
        )

    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO users (name, start_date) VALUES (?, ?)",
            ("DefaultUser", date.today().isoformat())
        )

    conn.commit()
    conn.close()


def get_default_user_id():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def insert_daily_log(user_id, mood, energy, stress, sleep_hours,
                     social_interaction, exercise_minutes, tasks_done):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO daily_logs
        (user_id, log_date, mood, energy, stress, sleep_hours,
         social_interaction, exercise_minutes, tasks_done)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, date.today().isoformat(), mood, energy, stress,
          sleep_hours, social_interaction, exercise_minutes, tasks_done))
    conn.commit()
    conn.close()


def get_latest_log(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT mood, energy, stress, sleep_hours, social_interaction, exercise_minutes
        FROM daily_logs WHERE user_id = ?
        ORDER BY log_date DESC LIMIT 1
    """, (user_id,))
    row = c.fetchone()
    conn.close()
    return row


def get_recent_logs(user_id, days=7):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT log_date, mood, energy, stress, sleep_hours,
               social_interaction, exercise_minutes, tasks_done
        FROM daily_logs WHERE user_id = ?
        ORDER BY log_date DESC LIMIT ?
    """, (user_id, days))
    rows = c.fetchall()
    conn.close()
    return rows


def get_all_tasks():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT task_id, name, category, difficulty, energy_required, social_level FROM tasks")
    rows = c.fetchall()
    conn.close()
    return rows


def get_recently_completed_task_ids(user_id, days=3):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT DISTINCT task_id FROM task_history
        WHERE user_id = ? AND completed = 1
        AND task_date >= date('now', ?)
    """, (user_id, f"-{days} days"))
    rows = c.fetchall()
    conn.close()
    return {r[0] for r in rows}


def insert_recommendation(user_id, task_id, reason):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO recommendations (user_id, task_id, rec_date, reason)
        VALUES (?, ?, ?, ?)
    """, (user_id, task_id, date.today().isoformat(), reason))
    conn.commit()
    conn.close()


def insert_task_history(user_id, task_id, completed=1):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO task_history (user_id, task_id, task_date, completed, completed_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, task_id, date.today().isoformat(),
          completed, datetime.now().isoformat()))
    conn.commit()
    conn.close()
