import os
import json
import asyncio
import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.prompt import Prompt
from rich.table import Table
from rich.align import Align
from rich.layout import Layout
from rich.text import Text
from rich.markdown import Markdown
from src.deep_research import DeepSearch
from google.api_core.exceptions import ResourceExhausted

console = Console()

def ensure_dirs():
    for folder in ["results", os.path.join("results", "reports"), os.path.join("results", "trees")]:
        os.makedirs(folder, exist_ok=True)

def save_json(data, filename, subfolder):
    path = os.path.join("results", subfolder, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path

def save_markdown(report, query):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = "".join(c for c in query if c.isalnum() or c in (" ", "_")).replace(" ", "_")
    filename = f"report_{safe_query}_{timestamp}.md"
    path = os.path.join("results", "reports", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    return path

def build_tree(node):
    tree = Tree(f"[bold green]{node.get('query', 'Recherche')}[/bold green]")
    def add_nodes(n, parent):
        for child in n.get("sub_queries", []):
            branch = parent.add(f"[cyan]{child.get('query')}[/cyan] - [magenta]{child.get('status')}[/magenta]")
            add_nodes(child, branch)
    add_nodes(node, tree)
    return tree

def display_tree(tree_data):
    tree = build_tree(tree_data)
    console.print(Panel(tree, title="[bold blue]Structure de Recherche", border_style="green"))

def display_dashboard(total, completed):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Total Queries", justify="center")
    table.add_column("Completed Queries", justify="center")
    table.add_row(str(total), str(completed))
    console.print(Panel(table, title="[bold blue]Dashboard", border_style="magenta"))

def count_nodes(node):
    total = 1
    completed = 1 if node.get("status") == "completed" else 0
    for child in node.get("sub_queries", []):
        t, c = count_nodes(child)
        total += t
        completed += c
    return total, completed

def header_panel():
    header_text = Text("RESEARCH LAB", style="bold bright_green on black", justify="center")
    return Panel(Align.center(header_text), border_style="bright_green", padding=(1, 2))

def ask_follow_up_questions(ds, initial_query):
    try:
        follow_up_questions = ds.generate_follow_up_questions(initial_query)
    except Exception as e:
        console.print(Panel(f"[red]Erreur lors de la génération des questions de suivi: {e}[/red]", border_style="red"))
        return []
    answers = []
    for question in follow_up_questions:
        answer = Prompt.ask(f"[bold yellow]{question}")
        answers.append({"question": question, "answer": answer})
    return answers

def combine_query(initial_query, follow_ups):
    qa_text = "\n".join([f"- {item['question']}: {item['answer']}" for item in follow_ups])
    combined = f"Initial query: {initial_query}\n\nFollow up Q&A:\n{qa_text}"
    return combined

def follow_up_notice(mode):
    if mode == "comprehensive":
        notice = Text("Le modèle Gemini a généré et intégré des questions de suivi pour affiner la recherche.", style="bold yellow")
        console.print(Panel(Align.center(notice), border_style="yellow"))

async def run_research(ds, query, breadth, depth):
    with Progress(SpinnerColumn(), BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), transient=True) as progress:
        task = progress.add_task("[bold green]Recherche en cours...", total=100)
        result = await ds.deep_research(query, breadth, depth)
        progress.update(task, completed=100)
    return result

async def main():
    ensure_dirs()
    load_dotenv()
    console.clear()
    layout = Layout()
    layout.split_column(
        Layout(header_panel(), name="header", size=3),
        Layout(name="body", ratio=1)
    )
    console.print(layout["header"])
    initial_query = Prompt.ask("[bold yellow]Entrez votre requête de recherche")
    mode = Prompt.ask("[bold yellow]Mode (fast, balanced, comprehensive)", choices=["fast", "balanced", "comprehensive"], default="comprehensive")
    breadth = int(Prompt.ask("[bold yellow]Largeur (breadth)", default="10"))
    depth = int(Prompt.ask("[bold yellow]Profondeur (depth)", default="5"))
    ds = DeepSearch(api_key=os.getenv("GEMINI_KEY"), mode=mode)
    
    console.print(Panel("[bold green]Génération des questions de suivi...[/bold green]", border_style="blue"))
    follow_up_answers = ask_follow_up_questions(ds, initial_query)
    if follow_up_answers:
        combined_query = combine_query(initial_query, follow_up_answers)
        console.print(Panel(f"[bold cyan]Requête combinée :\n{combined_query}", border_style="cyan"))
    else:
        combined_query = initial_query
    
    console.print(Panel("[bold green]Lancement de la recherche...[/bold green]", border_style="blue"))
    result = await run_research(ds, combined_query, breadth, depth)
    
    try:
        with open("research_tree.json", "r", encoding="utf-8") as f:
            tree_data = json.load(f)
    except Exception:
        tree_data = {}
    
    if tree_data:
        display_tree(tree_data)
        total, completed = count_nodes(tree_data)
        display_dashboard(total, completed)
        save_json(tree_data, f"research_tree_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "trees")
        follow_up_notice(mode)
    else:
        console.print(Panel("[red]Aucune arborescence disponible[/red]", border_style="red"))
    
    final_choice = Prompt.ask("[bold yellow]Générer le rapport final ? (O/N)", choices=["O", "N"], default="O")
    if final_choice.upper() == "O":
        learnings = result.get("learnings", [])
        visited_urls = result.get("visited_urls", {})
        console.print(Panel("[bold green]Génération du rapport final en cours...[/bold green]", border_style="blue"))
        try:
            report = ds.generate_final_report(combined_query, learnings, visited_urls)
            # Render the final report as Markdown for a classy look
            md_report = Markdown(report)
            console.print(Panel(md_report, title="[bold red]Rapport Final", border_style="green"))
            report_path = save_markdown(report, initial_query)
            console.print(Panel(f"[bold red]Rapport Final enregistré sous :[/bold red]\n{report_path}", border_style="green"))
        except ResourceExhausted as e:
            console.print(Panel(f"[red]Erreur: Ressource épuisée. Veuillez vérifier votre quota Gemini.\nDétails: {e}[/red]", border_style="red"))
        except Exception as e:
            console.print(Panel(f"[red]Erreur lors de la génération du rapport final: {e}[/red]", border_style="red"))
    else:
        console.print(Panel("[bold blue]Recherche terminée sans génération de rapport final[/bold blue]", border_style="blue"))

if __name__ == "__main__":
    asyncio.run(main())
