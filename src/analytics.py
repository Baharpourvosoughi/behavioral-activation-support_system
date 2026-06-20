# src/analytics.py

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from src.db import get_default_user_id, get_recent_logs

console = Console()


def show_analytics():
    user_id = get_default_user_id()
    logs = get_recent_logs(user_id, days=7)

    if not logs:
        console.print("[yellow]No data yet. Try logging a few days first.[/yellow]")
        return

    dates = [r[0] for r in logs]
    moods = [r[1] for r in logs]
    energies = [r[2] for r in logs]
    stresses = [r[3] for r in logs]
    sleeps = [r[4] for r in logs]

    avg_mood = sum(moods) / len(moods)
    avg_energy = sum(energies) / len(energies)
    avg_stress = sum(stresses) / len(stresses)
    avg_sleep = sum(sleeps) / len(sleeps)

    table = Table(title=f"Your last {len(logs)} days", border_style="blue")
    table.add_column("Date", style="dim")
    table.add_column("Mood", justify="center")
    table.add_column("Energy", justify="center")
    table.add_column("Stress", justify="center")
    table.add_column("Sleep h", justify="center")

    for r in reversed(logs):
        table.add_row(r[0], str(r[1]), str(r[2]), str(r[3]), str(r[4]))

    console.print(table)

    console.print(Panel(
        f"Avg mood: [bold]{avg_mood:.1f}[/bold]  |  "
        f"Avg energy: [bold]{avg_energy:.1f}[/bold]  |  "
        f"Avg stress: [bold]{avg_stress:.1f}[/bold]  |  "
        f"Avg sleep: [bold]{avg_sleep:.1f}h[/bold]",
        title="Weekly averages", border_style="cyan"
    ))

    latest = logs[0]
    console.print("\n[bold]Today's snapshot:[/bold]")
    with Progress(TextColumn("{task.description}"), BarColumn(), TextColumn("{task.fields[val]}"),
                  console=console) as progress:
        progress.add_task("Mood  ", total=10, completed=latest[1], val=f"{latest[1]}/10")
        progress.add_task("Energy", total=10, completed=latest[2], val=f"{latest[2]}/10")
        progress.add_task("Stress", total=10, completed=latest[3], val=f"{latest[3]}/10")

    insights = []

    if len(moods) >= 4:
        recent_mood = sum(moods[:3]) / 3
        older_mood = sum(moods[3:]) / len(moods[3:])
        if recent_mood > older_mood + 0.5:
            insights.append("Your mood has been improving lately.")
        elif recent_mood < older_mood - 0.5:
            insights.append("Your mood has dipped a bit recently. Be gentle with yourself.")

    if avg_stress >= 7:
        insights.append("Stress has been pretty high this week. Small breaks can help.")

    if avg_sleep < 6:
        insights.append("You're averaging under 6 hours of sleep — that catches up with you.")

    if avg_energy <= 4:
        insights.append("Energy has been low. It's okay to take on smaller tasks for now.")

    if insights:
        console.print("\n[bold]A few observations:[/bold]")
        for note in insights:
            console.print(f"  • {note}")
    else:
        console.print("\n[green]Things look fairly stable this week.[/green]")
