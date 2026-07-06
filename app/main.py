import sys
import webbrowser
import time
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.markdown import Markdown

from app.aggregator import get_briefing
from app.ai_service import start_adversarial_chat_session

console = Console()

def show_header():
    """Clear terminal and render a stylized visual header."""
    console.clear()
    title_text = Text()
    title_text.append("🌍 GLOBAL PERSPECTIVES ", style="bold red")
    title_text.append("| ", style="bold white")
    title_text.append("DAILY LONG-FORM BRIEFING", style="bold gold1")
    
    panel = Panel(
        Align.center(title_text),
        subtitle="[bold dim]AI-Synthesized Global Macro Intelligence Feed[/bold dim]",
        subtitle_align="center",
        border_style="red",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()

def show_synthesis_report(report_text: str):
    show_header()
    md = Markdown(report_text)
    panel = Panel(
        md,
        title="✨ [bold gold1]CROSS-CUTTING AI SYNTHESIS BRIEFING[/bold gold1]",
        border_style="bold gold1",
        padding=(1, 2),
        expand=False
    )
    console.print(panel)
    console.print()
    import questionary
    questionary.press_any_key_to_continue("👉 Press any key to return to the Main Menu...").ask()

def run_interrogation_loop(art):
    """Launches the live interactive adversarial chat window inside the terminal console."""
    import questionary
    
    show_header()
    console.print(Panel(
        f"Initializing critical link with Gemini 2.5 Flash...\nPrimes payload text from: [bold cyan]{art.title}[/bold cyan]",
        title="[bold red]🚨 ADVERSARIAL QA MODE[/bold red]",
        border_style="red"
    ))
    
    try:
        # Use full scraped text body if available; fallback cleanly to summary snippet
        content_payload = art.full_text if getattr(art, 'full_text', '') else art.summary
        chat_session = start_adversarial_chat_session(art.title, art.source, content_payload)
    except Exception as e:
        console.print(f"\n[bold red]Failed to boot AI Engine Session:[/bold red] {e}")
        time.sleep(3)
        return

    # Direct system priming greeting text
    show_header()
    console.print(Panel(
        f"You are now connected to the Intelligence Critic Engine for:\n'[italic]{art.title}'[/italic]\n\n"
        "[bold gold1]Suggested opening lines of inquiry:[/bold gold1]\n"
        " • 'What are the weakest analytical assumptions here?'\n"
        " • 'What critical counter-arguments did the author completely omit?'\n"
        " • 'How do these conclusions break down under an adversarial framework?'\n\n"
        "Type [bold red]'exit'[/bold red] or [bold red]'back'[/bold red] at any prompt to return to your dashboard layout.",
        title="[bold green]🥊 SYSTEM CHAT READY[/bold green]",
        border_style="green"
    ))

    while True:
        user_input = questionary.text(
            "🤔 Challenge Analysis:",
            style=questionary.Style([('question', 'fg:#ffd700 bold')])
        ).ask()
        
        if user_input is None:
            break
            
        clean_input = user_input.strip()
        if clean_input.lower() in ['exit', 'back', 'quit']:
            break
            
        if not clean_input:
            continue

        console.print()
        with console.status("[bold red]Stress-testing author claims & compiling counter-vectors...", spinner="earth"):
            try:
                response = chat_session.send_message(clean_input)
                reply_text = response.text
            except Exception as e:
                reply_text = f"**Pipeline Interruption Error:** Unable to stream token completions. {str(e)}"
        
        # Render response neatly wrapped inside a customized markdown canvas panel
        console.print(Panel(
            Markdown(reply_text),
            title=f"[bold red]AI Critic Response[/bold red]",
            border_style="red",
            padding=(1, 2)
        ))
        console.print()

def view_article(art):
    while True:
        show_header()
        pub_time_str = art.pub_date.strftime("%A, %b %d, %Y - %I:%M %p %Z")
        
        content_text = Text()
        content_text.append("Source: ", style="bold dim")
        content_text.append(f"{art.source}\n", style="bold italic cyan")
        content_text.append("Published: ", style="bold dim")
        content_text.append(f"{pub_time_str}\n", style="italic gray")
        content_text.append("Estimated Read Time: ", style="bold dim")
        content_text.append(f"⏱  {art.reading_time} minutes\n\n", style="bold green")
        
        content_text.append("AI Curated Deep-Dive Summary:\n", style="bold gold1")
        content_text.append(f"{art.summary}\n\n", style="white")
        
        panel = Panel(
            content_text,
            title=f"[bold yellow]{art.title}[/bold yellow]",
            border_style="bold red",
            padding=(1, 2),
            expand=False
        )
        console.print(panel)
        console.print()
        
        import questionary
        action = questionary.select(
            "What would you like to do with this article?",
            choices=[
                "💬 Interrogate This Analysis (Adversarial Q&A)",
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
        
        if action is None or "Back to Articles List" in action:
            return 'go_list'
        elif "Interrogate This Analysis" in action:
            run_interrogation_loop(art)
        elif "Open in default Web Browser" in action:
            webbrowser.open(art.url)
            time.sleep(1)
        elif "Back to Main Menu" in action:
            return 'go_main'

def read_briefing_menu(articles):
    while True:
        show_header()
        console.print("[bold white]Curated Strategic Deep Dives:[/bold white]")
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
            "Select an article to explore analysis vectors:",
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
    articles = []
    synthesis_report = ""
    was_expanded = False
    
    while True:
        show_header()
        
        if not articles:
            with console.status("[bold cyan]Scraping full text & compiling AI Synthesis Briefing... (Takes ~10s)", spinner="dots"):
                try:
                    articles, synthesis_report, was_expanded = get_briefing()
                except Exception as e:
                    console.print(f"[bold red]Error parsing briefing infrastructure:[/bold red] {e}")
                    articles, synthesis_report = [], ""
            
            show_header()
            if articles:
                if was_expanded:
                    console.print("[bold yellow]⚠ Quiet timeline news days detected. Expanded search parameters to 7 days.[/bold yellow]")
                else:
                    console.print("[bold green]✔ AI Executive Intelligence Briefing synthesized successfully.[/bold green]")
                console.print()
            else:
                console.print("[bold red]⚠ Processing Failure. Check terminal parameters or refresh.[/bold red]\n")
        
        choices = []
        if articles:
            choices.append("✨ View AI Cross-Cutting Synthesis Report")
            choices.append(f"📰 Read Curated Deep Dives ({len(articles)} articles)")
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
            articles = []
            synthesis_report = ""
            continue
            
        elif "View AI Cross-Cutting Synthesis Report" in selection:
            show_synthesis_report(synthesis_report)
            
        elif "Read Curated Deep Dives" in selection:
            read_briefing_menu(articles)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[italic gray]Exiting. Keep reading and stay informed! 🌍[/italic gray]\n")
        sys.exit(0)