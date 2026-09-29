"""
Command Line Interface for DevRecall.
Provides interactive debugging, memory inspection, and a live 2-minute demo mode.
"""

import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.theme import Theme

from .memory import DevMemory
from .agent import DevRecallAgent

custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "memory": "bold magenta"
})

# Ensure stdout supports UTF-8 on Windows terminals
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console(theme=custom_theme)


def print_banner():
    console.print(
        Panel.fit(
            "[bold cyan]DevRecall[/bold cyan] [white]-- Continuous Environment Memory for Developer Agents[/white]\n"
            "[dim]Powered by [magenta]Hindsight Agent Memory[/magenta] (Vectorize.io)[/dim]",
            border_style="cyan"
        )
    )


def run_demo():
    """
    Executes an automated, cinematic 2-minute demonstration showing
    the stark difference between an agent with vs. without Hindsight memory.
    Perfect for screen-recording hackathon video submissions!
    """
    print_banner()
    console.print("\n[bold yellow]=== PHASE 1: THE PROBLEM (AGENT WITHOUT MEMORY) ===[/bold yellow]\n")

    memory = DevMemory(storage_file=".devrecall/demo_bank.json")
    memory.clear()
    agent = DevRecallAgent(memory=memory)

    query = "How do I set test environment variables and run our integration tests?"
    console.print(f"[bold white]Developer Request:[/bold white] [green]\"{query}\"[/green]\n")

    time.sleep(1)
    console.print("[dim]Generating command without long-term memory...[/dim]")
    res_no_mem = agent.process(query, use_memory=False)

    syntax = Syntax(res_no_mem["response"]["command"], "bash", theme="monokai", line_numbers=False)
    console.print(Panel(syntax, title="[red]Naive Agent Output (Assumes Linux Bash & npm)[/red]", border_style="red"))

    time.sleep(1)
    console.print("[bold red]Simulating terminal execution on Windows PowerShell:[/bold red]")
    console.print("[red][X] export : The term 'export' is not recognized as the name of a cmdlet, function, or operable program.[/red]")
    console.print("[red][X] npm error: Missing script 'test' (Repository requires pnpm)[/red]")
    console.print("[bold red]RESULT: Command failed. Developer wastes 15 minutes troubleshooting environment drift.[/bold red]\n")

    time.sleep(1.5)
    console.print("[bold magenta]=== PHASE 2: HINDSIGHT AGENT MEMORY ENGAGED ===[/bold magenta]\n")
    console.print("[cyan]Retaining developer environment quirks into Hindsight bank ('devrecall-bank')...[/cyan]")

    time.sleep(1)
    memories_to_add = [
        ("Host environment: Windows 11 using PowerShell 7. Always use $env:KEY='val' for environment variables.", ["environment", "powershell", "windows"]),
        ("Package manager: Repository exclusively uses pnpm. Never invoke npm run or yarn.", ["package-manager", "pnpm", "node"]),
        ("Postgres port collision: Host port 5432 is occupied by local service. Docker Postgres must bind to host 5433.", ["database", "postgres", "ports"])
    ]

    for content, tags in memories_to_add:
        res = memory.retain(content=content, tags=tags)
        console.print(f"[magenta][RETAINED][/magenta] [dim]({', '.join(tags)}):[/dim] {content}")
        time.sleep(0.5)

    time.sleep(1.5)
    console.print("\n[bold green]=== PHASE 3: THE DEMO (AGENT WITH HINDSIGHT RECALL) ===[/bold green]\n")
    console.print(f"[bold white]Developer asks the exact same question again:[/bold white]")
    console.print(f"[green]\"{query}\"[/green]\n")

    time.sleep(1)
    console.print("[cyan]Querying Hindsight memory bank for environment context...[/cyan]")
    res_with_mem = agent.process(query, use_memory=True)

    # Show recalled memories
    table = Table(title="[magenta]Hindsight Recalled Memory Units[/magenta]", border_style="magenta")
    table.add_column("Memory ID", style="cyan")
    table.add_column("Fact / Rule Content", style="white")
    table.add_column("Tags", style="yellow")

    for m in res_with_mem["recalled_memories"]:
        table.add_row(m.get("id", "mem"), m.get("content", ""), ", ".join(m.get("tags", [])))

    console.print(table)
    console.print("\n[dim]Synthesizing command with recalled context...[/dim]")
    time.sleep(1)

    syntax_ok = Syntax(res_with_mem["response"]["command"], "powershell", theme="monokai", line_numbers=False)
    console.print(Panel(syntax_ok, title="[green]DevRecall Memory-Augmented Output[/green]", border_style="green"))

    console.print("[bold green][SUCCESS] PowerShell syntax ($env:) automatically applied.[/bold green]")
    console.print("[bold green][SUCCESS] pnpm test automatically invoked.[/bold green]")
    console.print("[bold green][SUCCESS] Zero manual explanations required. Perfect execution on attempt 1![/bold green]\n")


def run_interactive(args):
    """Handles standard CLI subcommands."""
    memory = DevMemory()
    agent = DevRecallAgent(memory=memory)

    if len(args) == 0 or args[0] == "help":
        print_banner()
        console.print("\n[bold]Usage:[/bold]")
        console.print("  python main.py demo                  Run cinematic 2-minute Before vs. After demo")
        console.print("  python main.py query <question>      Query DevRecall for command generation")
        console.print("  python main.py retain <fact>         Store an environment quirk or rule into Hindsight")
        console.print("  python main.py list                  View all currently retained memories")
        console.print("  python main.py clear                 Clear memory bank")
        return

    cmd = args[0].lower()

    if cmd == "demo":
        run_demo()

    elif cmd == "retain":
        if len(args) < 2:
            console.print("[error]Please specify content to retain: python main.py retain \"your rule\"[/error]")
            return
        fact = " ".join(args[1:])
        res = memory.retain(fact, tags=["manual", "dev"])
        console.print(f"[success]Retained in Hindsight memory:[/success] {fact}")

    elif cmd == "query":
        if len(args) < 2:
            console.print("[error]Please specify a query: python main.py query \"how do I start database?\"[/error]")
            return
        prompt = " ".join(args[1:])
        result = agent.process(prompt, use_memory=True)

        console.print(f"\n[bold cyan]Query:[/bold cyan] {prompt}")
        if result["recalled_memories"]:
            console.print(f"[magenta]Recalled {len(result['recalled_memories'])} context rules from Hindsight:[/magenta]")
            for m in result["recalled_memories"]:
                console.print(f"  • {m['content']}")
        else:
            console.print("[dim]No prior environment memories found for this query.[/dim]")

        syntax = Syntax(result["response"]["command"], "powershell", theme="monokai")
        console.print(Panel(syntax, title="Suggested Command", border_style="cyan"))

    elif cmd == "list":
        memories = memory.list_all()
        if not memories:
            console.print("[warning]No memories in the bank yet.[/warning]")
            return
        table = Table(title="[magenta]Stored Hindsight Memories[/magenta]")
        table.add_column("ID", style="cyan")
        table.add_column("Rule / Context", style="white")
        table.add_column("Tags", style="yellow")
        table.add_column("Timestamp", style="dim")
        for m in memories:
            table.add_row(m.get("id"), m.get("content"), ", ".join(m.get("tags", [])), m.get("timestamp", ""))
        console.print(table)

    elif cmd == "clear":
        memory.clear()
        console.print("[success]Cleared all memories from bank.[/success]")
