"""
CLI Components for Terminal Interface
Provides reusable terminal UI elements for the application
"""
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table
from rich.tree import Tree
from rich import print as rprint
from rich.markdown import Markdown

console = Console()

def display_header(title, subtitle=None):
    """Display a styled header with optional subtitle"""
    console.print(f"\n[bold blue]{title}[/]")
    if subtitle:
        console.print(f"[dim]{subtitle}[/]\n")

def display_card(title, content, style="blue"):
    """Display content in a styled card"""
    console.print(Panel(
        f"[bold]{title}[/]\n\n{content}",
        border_style=style
    ))

def display_progress_bar(completed, total, description="Progress"):
    """Display a styled progress bar with percentage"""
    percent = (completed / total * 100) if total > 0 else 0
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task(description, total=total)
        progress.update(task, completed=completed)

def display_status(title, description, status="in_progress"):
    """Display a status update with icon"""
    icons = {
        "in_progress": "🔄",
        "completed": "✅",
        "error": "❌"
    }
    styles = {
        "in_progress": "yellow",
        "completed": "green",
        "error": "red"
    }
    icon = icons.get(status, "•")
    style = styles.get(status, "blue")
    
    console.print(f"\n{icon} [bold {style}]{title}[/]")
    console.print(f"   {description}")

def display_metric_row(metrics):
    """
    Display a row of metrics
    
    Args:
        metrics: List of dicts with keys: value, label, color (optional)
    """
    table = Table(show_header=False, show_edge=False, box=None)
    for metric in metrics:
        color = metric.get('color', 'blue')
        table.add_row(
            f"[bold {color}]{metric['value']}[/]",
            f"[dim]{metric['label']}[/]"
        )
    console.print(table)

def display_research_tree(tree_data, level=0):
    """Display a text-based research tree"""
    if not tree_data:
        return console.print("[yellow]No research tree data available.[/]")
    
    prefix = "  " * level
    status_color = "green" if tree_data.get("status") == "completed" else "yellow"
    icon = "✅" if tree_data.get("status") == "completed" else "🔄"
    
    query = tree_data.get("query", "")[:50] + ("..." if len(tree_data.get("query", "")) > 50 else "")
    console.print(f"{prefix}{icon} [bold {status_color}]{query}[/]")
    console.print(f"{prefix}  [dim]Depth: {tree_data.get('depth', 0)} | Learnings: {len(tree_data.get('learnings', []))}[/]")
    
    for child in tree_data.get("sub_queries", []):
        display_research_tree(child, level + 1)

def display_learnings(learnings):
    """Display research learnings in a nice format"""
    console.print("\n[bold blue]Key Learnings & Insights[/]")
    for i, learning in enumerate(learnings, 1):
        console.print(Panel(
            learning,
            title=f"Learning {i}",
            border_style="blue"
        ))

def display_sources(sources):
    """Display research sources in a table format"""
    if not sources:
        return console.print("[yellow]No sources available.[/]")
    
    table = Table(title="Research Sources")
    table.add_column("Source", style="blue")
    table.add_column("Type", style="cyan")
    table.add_column("Relevance", justify="right", style="green")
    
    for source in sources:
        table.add_row(
            source.get("url", "N/A"),
            source.get("type", "Unknown"),
            f"{source.get('relevance', 0)}%"
        )
    
    console.print(table)

def display_research_summary(results):
    """Display a summary of research results"""
    stats = [
        {"value": len(results.get("learnings", [])), "label": "Key Insights", "color": "green"},
        {"value": len(results.get("visited_urls", {})), "label": "Sources Referenced", "color": "blue"},
        {"value": f"{results.get('breadth', 0)}/10", "label": "Research Breadth", "color": "yellow"},
        {"value": f"{results.get('depth', 0)}/5", "label": "Research Depth", "color": "magenta"}
    ]
    
    console.print("\n[bold]Research Summary[/]")
    display_metric_row(stats)