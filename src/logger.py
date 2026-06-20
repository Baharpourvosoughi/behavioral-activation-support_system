# src/logger.py

from rich.console import Console
from rich.panel import Panel
from src.db import get_default_user_id, insert_daily_log

console = Console()


def ask_int(prompt, min_val, max_val):
    while True:
        try:
            val = int(console.input(prompt))
            if min_val <= val <= max_val:
                return val
            console.print(f"[red]Please enter a number between {min_val} and {max_val}.[/red]")
        except ValueError:
            console.print("[red]That doesn't look like a number. Try again.[/red]")


def ask_float(prompt, min_val, max_val):
    while True:
        try:
            val = float(console.input(prompt))
            if min_val <= val <= max_val:
                return val
            console.print(f"[red]Please enter a value between {min_val} and {max_val}.[/red]")
        except ValueError:
            console.print("[red]That doesn't look right. Try again.[/red]")


def log_daily():
    console.print(Panel.fit(
        "[bold]Daily Check-in[/bold]\n[dim]Rate things as honestly as you can.[/dim]",
        border_style="blue"
    ))

    console.print("\n[dim]Scale: 1 = very low, 10 = very high[/dim]\n")

    mood = ask_int("How's your mood today? (1–10): ", 1, 10)
    energy = ask_int("Energy level? (1–10): ", 1, 10)
    stress = ask_int("How stressed do you feel? (1–10): ", 1, 10)
    sleep = ask_float("Hours of sleep last night? (0–24): ", 0, 24)
    social = ask_int("Did you interact with people today? (1 = barely, 5 = a lot): ", 1, 5)
    exercise = ask_int("Minutes of any physical activity? (0–300): ", 0, 300)
    tasks = ask_int("How many tasks did you get done today? (0–20): ", 0, 20)

    user_id = get_default_user_id()
    insert_daily_log(user_id, mood, energy, stress, sleep, social, exercise, tasks)

    console.print("\n[green]Logged. Good job checking in.[/green]")
