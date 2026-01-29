#!/usr/bin/env python3
"""CLI for ResearchSwarm."""

import os
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

from .coordinator import ResearchSwarm


console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """🐝 ResearchSwarm - Multi-agent research system."""
    pass


@cli.command()
@click.argument("query")
@click.option("--depth", "-d", default="standard", type=click.Choice(["quick", "standard", "deep"]), help="Research depth")
@click.option("--output", "-o", help="Output file path")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
def research(query, depth, output, json_output):
    """Run a research query."""
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]Error: OPENAI_API_KEY environment variable not set[/red]")
        sys.exit(1)
    
    console.print(Panel.fit(
        f"[bold blue]🐝 ResearchSwarm[/bold blue]\n"
        f"Query: {query[:80]}{'...' if len(query) > 80 else ''}\n"
        f"Depth: {depth}",
        border_style="blue"
    ))
    
    swarm = ResearchSwarm()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Research in progress...", total=None)
        result = swarm.research(query, depth=depth)
    
    console.print(f"\n[dim]Completed in {result.duration_seconds:.1f}s using {len(result.agent_outputs)} agents[/dim]\n")
    
    if json_output:
        import json
        output_str = json.dumps(result.to_dict(), indent=2, default=str)
        if output:
            with open(output, "w") as f:
                f.write(output_str)
            console.print(f"[green]✓ Saved to {output}[/green]")
        else:
            console.print(output_str)
    else:
        console.print(Markdown(result.report))
        
        if output:
            with open(output, "w") as f:
                f.write(result.report)
            console.print(f"\n[green]✓ Saved to {output}[/green]")
    
    # Show sources
    if result.sources:
        console.print(f"\n[bold]Sources ({len(result.sources)}):[/bold]")
        for i, source in enumerate(result.sources[:10], 1):
            console.print(f"[dim]{i}. {source}[/dim]")


@cli.command()
def chat():
    """Interactive research chat."""
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]Error: OPENAI_API_KEY environment variable not set[/red]")
        sys.exit(1)
    
    console.print(Panel.fit(
        "[bold blue]🐝 ResearchSwarm Chat[/bold blue]\n"
        "Ask any research question. Type 'quit' to exit.\n"
        "Prefix with 'deep:' for deep research.",
        border_style="blue"
    ))
    
    swarm = ResearchSwarm()
    
    while True:
        try:
            query = console.input("\n[bold green]You:[/bold green] ")
            
            if query.lower() in ("quit", "exit", "q"):
                console.print("[dim]Goodbye![/dim]")
                break
            
            if not query.strip():
                continue
            
            # Check for depth prefix
            depth = "quick"
            if query.lower().startswith("deep:"):
                depth = "deep"
                query = query[5:].strip()
            elif query.lower().startswith("standard:"):
                depth = "standard"
                query = query[9:].strip()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Researching ({depth})...", total=None)
                result = swarm.research(query, depth=depth)
            
            console.print(f"\n[bold blue]Research Report:[/bold blue] [dim]({result.duration_seconds:.1f}s)[/dim]\n")
            console.print(Markdown(result.report))
            
        except KeyboardInterrupt:
            console.print("\n[dim]Goodbye![/dim]")
            break


@cli.command()
def agents():
    """List available agents."""
    swarm = ResearchSwarm.__new__(ResearchSwarm)
    swarm.agents = {}
    
    from .agents import SearchAgent, DataAgent, LiteratureAgent, CriticAgent, SynthesisAgent
    
    agents_info = [
        ("search", SearchAgent, "Searches the web for relevant information"),
        ("data", DataAgent, "Extracts statistics and structured data"),
        ("literature", LiteratureAgent, "Reviews academic and industry literature"),
        ("critic", CriticAgent, "Provides critical analysis and counterarguments"),
        ("synthesis", SynthesisAgent, "Combines findings into a coherent report"),
    ]
    
    console.print("\n[bold]Available Agents:[/bold]\n")
    
    for name, cls, desc in agents_info:
        console.print(f"  [cyan]{name:12}[/cyan] {desc}")
    
    console.print("\n[bold]Research Depths:[/bold]\n")
    console.print("  [cyan]quick[/cyan]      2 agents (search + synthesis) - ~30s")
    console.print("  [cyan]standard[/cyan]   4 agents - ~2min")
    console.print("  [cyan]deep[/cyan]       5 agents (includes critic) - ~5min")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
