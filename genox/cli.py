import asyncio
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from genox.brain.agent import agent
from genox.tools.base import registry

console = Console()

async def run_cli_loop():
    console.print(Panel.fit(
        "[bold cyan]G.E.N.O.X. CORE ONLINE[/bold cyan]\n"
        "[dim]Universal Autonomous Agent Console (Powered by Google Gemini)[/dim]\n"
        f"[green]Registered Tools: {len(registry.get_all_tools())}[/green] | Model: [yellow]{agent.model_name}[/yellow]",
        border_style="cyan"
    ))

    if not agent.api_key:
        console.print("[bold red]Warning:[/bold red] No GEMINI_API_KEY found in environment or .env file.")
        key = console.input("[yellow]Enter your Google AI Studio API Key (or press enter to skip): [/yellow]").strip()
        if key:
            agent.update_key(key)
            console.print("[green]API Key configured successfully![/green]")

    while True:
        try:
            prompt = console.input("\n[bold cyan]Genox ➔ [/bold cyan]").strip()
            if not prompt:
                continue
            if prompt.lower() in ("exit", "quit", "q"):
                console.print("[yellow]Shutting down Genox. Goodbye![/yellow]")
                break

            console.print(f"[dim]Dispatching task...[/dim]")

            async for event in agent.execute_task(prompt=prompt):
                event_type = event.get("type")

                if event_type == "thought":
                    console.print(Panel(
                        event["content"],
                        title="[bold magenta]🧠 Thought[/bold magenta]",
                        border_style="magenta",
                        expand=False
                    ))
                elif event_type == "tool_call":
                    args_text = str(event.get("args", {}))
                    console.print(Panel(
                        f"[bold yellow]Tool:[/bold yellow] {event['tool']}\n[bold yellow]Args:[/bold yellow] {args_text}",
                        title=f"[bold cyan]⚙️ Tool Call (Step {event.get('step')})[/bold cyan]",
                        border_style="cyan",
                        expand=False
                    ))
                elif event_type == "tool_result":
                    output_snippet = event["output"]
                    if len(output_snippet) > 800:
                        output_snippet = output_snippet[:800] + "\n... [truncated]"
                    console.print(Panel(
                        output_snippet,
                        title=f"[bold green]✓ Result: {event['tool']}[/bold green]",
                        border_style="green",
                        expand=False
                    ))
                elif event_type == "final_response":
                    console.print("\n" + "="*50)
                    console.print(Markdown(event["content"]))
                    console.print("="*50 + "\n")
                elif event_type == "error":
                    console.print(f"[bold red]Alert:[/bold red] {event.get('message')}")

        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Interrupted. Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]CLI Error:[/bold red] {e}")

def main():
    asyncio.run(run_cli_loop())

if __name__ == "__main__":
    main()
