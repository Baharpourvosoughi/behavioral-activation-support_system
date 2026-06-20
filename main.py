# main.py

from rich.console import Console
from rich.panel import Panel
from src.db import init_db

console = Console()

def main():
    # set up the database tables if they don't exist yet
    init_db()

    console.print(Panel.fit(
        "[bold cyan]Behavioral Activation System[/bold cyan]\n"
        "[dim]A small personal project to track mood and stay active[/dim]",
        border_style="cyan"
    ))

    while True:
        console.print("\nWhat do you want to do?")
        console.print("  [bold]1.[/bold] Log today's data")
        console.print("  [bold]2.[/bold] Get task suggestions")
        console.print("  [bold]3.[/bold] See my weekly trends")
        console.print("  [bold]4.[/bold] Exit")

        choice = console.input("\n[bold yellow]Your choice:[/bold yellow] ").strip()

        if choice == "1":
            from src.logger import log_daily
            log_daily()
        elif choice == "2":
            from src.recommender import recommend
            recommend()
        elif choice == "3":
            from src.analytics import show_analytics
            show_analytics()
        elif choice == "4":
            console.print("\n[dim]See you tomorrow. Take care.[/dim]")
            break
        else:
            console.print("[red]Just enter 1, 2, 3, or 4.[/red]")

if __name__ == "__main__":
    main()
