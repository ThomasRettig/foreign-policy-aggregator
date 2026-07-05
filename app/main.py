import sys
import webbrowser
import time
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

from app.aggregator import get_briefing

console = Console()

def show_header():
    """Clear terminal and render a stylized visual header."""
    console.clear()
    
    # Sleek header banner
    title_text = Text()
    title_text.append("🌍 GLOBAL PERSPECTIVES ", style="bold red")
    title_text.append("| ", style="bold white")
    title_text.append("DAILY LONG-FORM BRIEFING", style="bold gold1")
    
    panel = Panel(
        Align.center(title_text),
        subtitle="[bold dim]Yesterday & Today's Premium Foreign Policy Analysis[/bold dim]",
        subtitle_align="center",
        border_style="red",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()

def view_article(art):
    """Display the full article details card and handle actions."""
    while True:
        show_header()
        
        # Nicely formatted publication time in local format
        pub_time_str = art.pub_date.strftime("%A, %b %d, %Y - %I:%M %p %Z")
        
        # Article metadata section
        content_text = Text()
        content_text.append("Source: ", style="bold dim")
        content_text.append(f"{art.source}\n", style="bold italic cyan")
        content_text.append("Published: ", style="bold dim")
        content_text.append(f"{pub_time_str}\n", style="italic gray")
        content_text.append("Estimated Read Time: ", style="bold dim")
        content_text.append(f"⏱  {art.reading_time} minutes\n\n", style="bold green")
        
        # Clean 2-sentence summary
        content_text.append("Summary:\n", style="bold gold1")
        content_text.append(f"{art.summary}\n\n", style="white")
        
        # Clickable URL
        content_text.append("URL: ", style="bold dim")
        content_text.append(f"{art.url}\n", style="underline blue")
        
        panel = Panel(
            content_text,
            title=f"[bold yellow]{art.title}[/bold yellow]",
            border_style="bold red",
            padding=(1, 2),
            expand=False
        )
        
        console.print(panel)
        console.print()
        
        # Action choices for the selected article
        import questionary
        action = questionary.select(
            "What would you like to do with this article?",
            choices=[
                "🌐 Open in default Web Browser",
                "👈 Back to Articles List",
                "🏠 Back to Main Menu"
            ],
            style=questionary.Style([
                ('qmark', 'fg:#e5200f bold'),
                ('pointer', 'fg:#e5200f bold'),
                ('highlighted', 'fg:#ffffff bg:#e5200f bold'),
            ])
        ).ask()
        
        if action is None:
            return 'go_list'
        elif "Open in default Web Browser" in action:
            console.print(f"\n[green]Opening browser for:[/green] {art.title}...")
            webbrowser.open(art.url)
            time.sleep(1)
        elif "Back to Articles List" in action:
            return 'go_list'
        elif "Back to Main Menu" in action:
            return 'go_main'

def read_briefing_menu(articles):
    """Render the scrollable list of article options."""
    while True:
        show_header()
        console.print("[bold white]Latest Long-Form Briefing:[/bold white]")
        console.print()
        
        import questionary
        choices = []
        for i, art in enumerate(articles):
            choices.append(
                questionary.Choice(
                    title=f"[{art.source}] {art.title} ({art.reading_time} min read)",
                    value=i
                )
            )
        choices.append(questionary.Choice(title="<- Back to Main Menu", value=-1))
        
        idx = questionary.select(
            "Select an article to read summary:",
            choices=choices,
            style=questionary.Style([
                ('qmark', 'fg:#e5200f bold'),
                ('pointer', 'fg:#e5200f bold'),
                ('highlighted', 'fg:#ffffff bg:#e5200f bold'),
            ])
        ).ask()
        
        if idx is None or idx == -1:
            break
            
        res = view_article(articles[idx])
        if res == 'go_main':
            break

def main():
    """Main application loop."""
    articles = []
    was_expanded = False
    
    while True:
        show_header()
        
        # Load and parse articles if not already loaded
        if not articles:
            with console.status("[bold cyan]Fetching and validating top foreign policy articles... (this may take up to 10s)", spinner="dots"):
                try:
                    articles, was_expanded = get_briefing()
                except Exception as e:
                    console.print(f"[bold red]Error fetching briefing:[/bold red] {e}")
                    articles = []
            
            show_header()
            if articles:
                if was_expanded:
                    console.print("[bold yellow]⚠ Quiet news days detected. Expanded search to the past 7 days.[/bold yellow]")
                else:
                    console.print("[bold green]✔ Briefing loaded successfully for today & yesterday.[/bold green]")
                console.print()
            else:
                console.print("[bold red]⚠ No long-form articles found. Please check your network or try refreshing.[/bold red]\n")
        
        # Setup Main Menu choices
        choices = []
        if articles:
            choices.append(f"📰 Read Latest Briefing ({len(articles)} articles)")
        choices.extend([
            "🔄 Refresh Feed",
            "❌ Exit"
        ])
        
        import questionary
        selection = questionary.select(
            "What would you like to do?",
            choices=choices,
            style=questionary.Style([
                ('qmark', 'fg:#e5200f bold'),
                ('question', 'bold'),
                ('answer', 'fg:#e5200f bold'),
                ('pointer', 'fg:#e5200f bold'),
                ('highlighted', 'fg:#ffffff bg:#e5200f bold'),
                ('selected', 'fg:#e5200f'),
            ])
        ).ask()
        
        if not selection or "Exit" in selection:
            console.print("\n[italic gray]Exiting. Keep reading and stay informed! 🌍[/italic gray]\n")
            sys.exit(0)
            
        elif "Refresh" in selection:
            articles = []  # Triggers feed reload
            continue
            
        elif "Read Latest Briefing" in selection:
            read_briefing_menu(articles)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[italic gray]Exiting. Keep reading and stay informed! 🌍[/italic gray]\n")
        sys.exit(0)
