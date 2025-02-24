import os
import json
import asyncio
import datetime
import time
import webbrowser
import uuid
from pathlib import Path

# Dépendances externes
from dotenv import load_dotenv
from rich.console import Console, Group
from rich.panel import Panel
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.align import Align
from rich.layout import Layout
from rich.text import Text
from rich.markdown import Markdown
from rich.box import HEAVY
from rich.style import Style
from rich import print as rprint
from src.deep_research import DeepSearch
from google.api_core.exceptions import ResourceExhausted

# Configuration globale
APP_NAME = "LABORATOIRE DE RECHERCHE GEMINI"
APP_VERSION = "1.0.0"

# Chemins d'accès
BASE_DIR = Path("results")
REPORTS_DIR = BASE_DIR / "reports"
TREES_DIR = BASE_DIR / "trees"

# Initialisation console
console = Console()

# Couleurs du thème
THEME = {
    "header_bg": "bright_blue",
    "header_fg": "black",
    "header_border": "bright_blue",
    "panel_border": "cyan",
    "tree_border": "green",
    "dashboard_border": "magenta",
    "stats_border": "yellow",
    "help_border": "bright_blue",
    "success_color": "bright_green",
    "error_color": "bright_red",
    "warning_color": "bright_yellow",
    "info_color": "bright_cyan",
    "query_color": "bright_magenta",
    "status_completed": "bright_green",
    "status_in_progress": "bright_yellow",
    "status_waiting": "bright_cyan",
    "box_style": HEAVY
}

# Traductions
TRANSLATION = {
    "app_title": "LABORATOIRE DE RECHERCHE GEMINI",
    "welcome": "Bienvenue dans votre laboratoire de recherche intelligent",
    "enter_query": "Entrez votre requête de recherche",
    "select_mode": "Sélectionnez le mode de recherche",
    "select_breadth": "Largeur de recherche (nombre de requêtes parallèles)",
    "select_depth": "Profondeur de recherche (niveaux d'exploration)",
    "generating_questions": "Génération des questions de suivi...",
    "combined_query": "Requête combinée :",
    "launching_research": "Lancement de la recherche approfondie...",
    "research_in_progress": "Recherche en cours...",
    "no_tree": "Aucune arborescence disponible",
    "generate_report": "Générer le rapport final ?",
    "generating_report": "Génération du rapport final en cours...",
    "report_saved": "Rapport Final enregistré sous :",
    "research_completed": "Recherche terminée sans génération de rapport final",
    "error_quota": "Erreur: Ressource épuisée. Veuillez vérifier votre quota Gemini.",
    "error_questions": "Erreur lors de la génération des questions de suivi",
    "error_report": "Erreur lors de la génération du rapport final",
    "research_structure": "Structure de Recherche",
    "dashboard": "Tableau de Bord",
    "stats": "Statistiques",
    "total_queries": "Requêtes Totales",
    "completed_queries": "Requêtes Complétées",
    "research_depth": "Profondeur Actuelle",
    "elapsed_time": "Temps Écoulé",
    "sources_found": "Sources Trouvées",
    "knowledge_points": "Points de Connaissance",
    "help_mode_fast": "RAPIDE: Recherche superficielle (1-3 min)",
    "help_mode_balanced": "ÉQUILIBRÉ: Compromis vitesse/profondeur (3-6 min)",
    "help_mode_comprehensive": "EXHAUSTIF: Analyse complète, récursive (5-12 min)",
    "yes": "Oui",
    "no": "Non",
    "open_report": "Ouvrir le rapport dans votre navigateur ?",
    "follow_up_notice": "Le modèle Gemini a généré et intégré des questions de suivi pour affiner la recherche.",
    "final_report": "Rapport Final",
    "source_network": "Réseau de Sources",
    "knowledge_map": "Carte des Connaissances",
    "loading": "Chargement...",
    "export_html": "Exporter en HTML",
    "export_json": "Exporter en JSON",
    "search_status": "État de la Recherche",
    "generate_graph": "Générer le graphique des connaissances ?",
    "generating_graph": "Génération du graphique de connaissances...",
    "graph_generated": "Graphique généré avec succès",
    "open_graph": "Ouvrir le graphique dans votre navigateur ?",
    "report_browser_opened": "Rapport ouvert dans votre navigateur.",
    "graph_browser_opened": "Graphique ouvert dans votre navigateur."
}

# Fonctions utilitaires
def ensure_dirs():
    """Crée tous les répertoires nécessaires"""
    for folder in [BASE_DIR, REPORTS_DIR, TREES_DIR]:
        folder.mkdir(exist_ok=True, parents=True)

def format_elapsed_time(seconds):
    """Formate le temps écoulé en heures, minutes, secondes"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(seconds)}s"

def save_json(data, filename, subfolder):
    """Sauvegarde des données JSON avec gestion d'erreurs améliorée"""
    path = BASE_DIR / subfolder / filename
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return str(path)
    except Exception as e:
        console.print(f"[{THEME['error_color']}]Erreur lors de la sauvegarde JSON: {e}[/{THEME['error_color']}]")
        return None

def save_markdown(report, query):
    """Sauvegarde le rapport markdown avec formatage du nom de fichier"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = "".join(c for c in query if c.isalnum() or c in (" ", "_")).replace(" ", "_")
    # Limiter la longueur du nom de fichier
    safe_query = safe_query[:50] + "..." if len(safe_query) > 50 else safe_query
    filename = f"report_{safe_query}_{timestamp}.md"
    path = REPORTS_DIR / filename
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(report)
        return str(path)
    except Exception as e:
        console.print(f"[{THEME['error_color']}]Erreur lors de la sauvegarde du rapport: {e}[/{THEME['error_color']}]")
        return None

def export_html(markdown_path, query):
    """Exporte le rapport Markdown en HTML"""
    if not markdown_path or not os.path.exists(markdown_path):
        return None
    
    html_path = markdown_path.replace(".md", ".html")
    try:
        with open(markdown_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()
        
        # Création d'un HTML basique avec style
        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport de recherche: {query}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 1.5em;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        code {{
            background-color: #f8f8f8;
            padding: 2px 4px;
            border-radius: 3px;
        }}
        pre {{
            background-color: #f8f8f8;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-left: 0;
            color: #666;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            border: 1px solid #ddd;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
        .date {{
            color: #7f8c8d;
            font-style: italic;
        }}
        /* Ajout de classes pour la mise en page avancée */
        .highlight {{
            background-color: #ffffcc;
            padding: 2px;
        }}
        .note {{
            background-color: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }}
        .warning {{
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <div class="date">{datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}</div>
    <div id="content">
    <!-- Contenu Markdown converti -->
    
    </div>
    <script>
    // Charger la bibliothèque Markdown-it depuis un CDN
    document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/markdown-it/12.3.2/markdown-it.min.js"><\\/script>');
    window.onload = function() {{
        // Initialiser markdown-it
        const md = window.markdownit({{
            html: true,
            linkify: true,
            typographer: true
        }});
        
        // Convertir le Markdown en HTML
        const markdownContent = `{markdown_content.replace('`', '\\`')}`;
        const htmlContent = md.render(markdownContent);
        
        // Insérer dans la page
        document.getElementById('content').innerHTML = htmlContent;
    }};
    </script>
</body>
</html>"""
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return html_path
    except Exception as e:
        console.print(f"[{THEME['error_color']}]Erreur lors de l'exportation HTML: {e}[/{THEME['error_color']}]")
        return None

def open_file(path):
    """Ouvre un fichier avec l'application par défaut du système"""
    try:
        if os.path.exists(path):
            webbrowser.open(f"file://{os.path.abspath(path)}")
            return True
        return False
    except Exception as e:
        console.print(f"[{THEME['error_color']}]Erreur lors de l'ouverture du fichier: {e}[/{THEME['error_color']}]")
        return False

# Système de visualisation avancée des connaissances
def generate_knowledge_graph(tree_data, visited_urls):
    """Génère un graphique de connaissances au format HTML/JS utilisant d3.js"""
    if not tree_data:
        return None
    
    # Extraire les nœuds (requêtes) et les points de connaissance
    nodes = []
    links = []
    learnings = []
    
    def extract_nodes(node, parent_id=None):
        node_id = node.get("id", str(uuid.uuid4()))
        node_type = "query"
        node_label = node.get("query", "Unknown")
        node_status = node.get("status", "waiting")
        
        # Ajouter le nœud principal
        nodes.append({
            "id": node_id,
            "label": node_label,
            "type": node_type,
            "status": node_status
        })
        
        # Ajouter le lien avec le parent si applicable
        if parent_id:
            links.append({
                "source": parent_id,
                "target": node_id,
                "value": 2
            })
        
        # Ajouter les connaissances acquises
        for i, learning in enumerate(node.get("learnings", [])):
            learning_id = f"learning_{node_id}_{i}"
            # Tronquer la connaissance si trop longue
            short_learning = learning[:100] + "..." if len(learning) > 100 else learning
            
            # Ajouter le nœud de connaissance
            nodes.append({
                "id": learning_id,
                "label": short_learning,
                "type": "learning",
                "full_text": learning
            })
            
            # Lier la connaissance à la requête
            links.append({
                "source": node_id,
                "target": learning_id,
                "value": 1
            })
            
            learnings.append({
                "id": learning_id,
                "text": learning,
                "query": node_label
            })
        
        # Traiter récursivement les sous-requêtes
        for child in node.get("sub_queries", []):
            extract_nodes(child, node_id)
    
    # Démarrer l'extraction depuis la racine
    extract_nodes(tree_data)
    
    # Ajouter les sources comme nœuds
    for i, (url_id, url_data) in enumerate(visited_urls.items()):
        source_id = f"source_{i}"
        source_title = url_data.get('title', 'Unknown Source')
        source_link = url_data.get('link', '#')
        
        # Ajouter le nœud de source
        nodes.append({
            "id": source_id,
            "label": source_title,
            "type": "source",
            "url": source_link
        })
        
        # Lier avec quelques connaissances pertinentes (simulation)
        # Dans une implémentation réelle, on aurait une correspondance exacte
        if learnings and i < len(learnings):
            links.append({
                "source": source_id,
                "target": learnings[i]["id"],
                "value": 1
            })
    
    # Générer le HTML pour le graphique de connaissances
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Graphique des Connaissances</title>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                overflow: hidden;
                background-color: #f8f9fa;
            }}
            #graph {{
                width: 100vw;
                height: 100vh;
            }}
            .node {{
                stroke: #fff;
                stroke-width: 1.5px;
            }}
            .link {{
                stroke: #999;
                stroke-opacity: 0.6;
            }}
            .node-query {{
                fill: #3498db;
            }}
            .node-learning {{
                fill: #2ecc71;
            }}
            .node-source {{
                fill: #e74c3c;
            }}
            .status-completed {{
                stroke: #2ecc71;
                stroke-width: 3px;
            }}
            .status-in_progress {{
                stroke: #f39c12;
                stroke-width: 3px;
            }}
            .status-waiting {{
                stroke: #95a5a6;
                stroke-width: 3px;
            }}
            .tooltip {{
                position: absolute;
                background-color: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                max-width: 300px;
                z-index: 1000;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s;
            }}
            .controls {{
                position: absolute;
                top: 10px;
                left: 10px;
                background-color: rgba(255, 255, 255, 0.8);
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            button {{
                margin: 5px;
                padding: 5px 10px;
                background-color: #3498db;
                border: none;
                color: white;
                border-radius: 3px;
                cursor: pointer;
            }}
            button:hover {{
                background-color: #2980b9;
            }}
        </style>
    </head>
    <body>
        <div id="graph"></div>
        <div class="tooltip" id="tooltip"></div>
        <div class="controls">
            <button id="btnZoomIn">Zoom +</button>
            <button id="btnZoomOut">Zoom -</button>
            <button id="btnReset">Reset</button>
            <button id="btnToggleQueries">Requêtes</button>
            <button id="btnToggleLearnings">Connaissances</button>
            <button id="btnToggleSources">Sources</button>
        </div>

        <script>
            // Données du graphique
            const nodes = {json.dumps(nodes)};
            const links = {json.dumps(links)};
            
            // Configuration
            const width = window.innerWidth;
            const height = window.innerHeight;
            const tooltip = d3.select("#tooltip");
            
            // Créer le SVG
            const svg = d3.select("#graph")
                .append("svg")
                .attr("width", width)
                .attr("height", height);
                
            // Groupe pour zoom/pan
            const g = svg.append("g");
            
            // Zoom behavior
            const zoom = d3.zoom()
                .scaleExtent([0.1, 4])
                .on("zoom", (event) => {{
                    g.attr("transform", event.transform);
                }});
                
            svg.call(zoom);
            
            // Simulation de forces
            const simulation = d3.forceSimulation(nodes)
                .force("link", d3.forceLink(links).id(d => d.id).distance(100))
                .force("charge", d3.forceManyBody().strength(-300))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collision", d3.forceCollide().radius(50));
            
            // Lignes pour les liens
            const link = g.append("g")
                .selectAll("line")
                .data(links)
                .enter()
                .append("line")
                .attr("class", "link")
                .attr("stroke-width", d => d.value);
            
            // Nœuds
            const node = g.append("g")
                .selectAll("circle")
                .data(nodes)
                .enter()
                .append("circle")
                .attr("class", d => `node node-${{d.type}} status-${{d.status || 'normal'}}`)
                .attr("r", d => d.type === "query" ? 15 : (d.type === "source" ? 12 : 8))
                .on("mouseover", function(event, d) {{
                    // Afficher info-bulle
                    tooltip.style("opacity", 1)
                        .html(`<strong>${{d.type === "query" ? "Requête" : (d.type === "source" ? "Source" : "Connaissance")}}</strong><br>${{d.full_text || d.label}}`)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 20) + "px");
                }})
                .on("mouseout", function() {{
                    // Cacher info-bulle
                    tooltip.style("opacity", 0);
                }})
                .on("click", function(event, d) {{
                    if (d.type === "source" && d.url) {{
                        window.open(d.url, '_blank');
                    }}
                }})
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));
            
            // Étiquettes de texte
            const text = g.append("g")
                .selectAll("text")
                .data(nodes)
                .enter()
                .append("text")
                .text(d => {{
                    const shortLabel = d.label.length > 20 ? d.label.substring(0, 20) + "..." : d.label;
                    return shortLabel;
                }})
                .attr("dy", 25)
                .attr("text-anchor", "middle")
                .attr("font-size", "10px");
            
            // Mise à jour de la position lors de la simulation
            simulation.on("tick", () => {{
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);
                
                node
                    .attr("cx", d => d.x = Math.max(20, Math.min(width - 20, d.x)))
                    .attr("cy", d => d.y = Math.max(20, Math.min(height - 20, d.y)));
                
                text
                    .attr("x", d => d.x)
                    .attr("y", d => d.y);
            }});
            
            // Fonctions drag
            function dragstarted(event, d) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }}
            
            function dragged(event, d) {{
                d.fx = event.x;
                d.fy = event.y;
            }}
            
            function dragended(event, d) {{
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }}
            
            // Contrôles
            document.getElementById("btnZoomIn").addEventListener("click", () => {{
                svg.transition().call(zoom.scaleBy, 1.5);
            }});
            
            document.getElementById("btnZoomOut").addEventListener("click", () => {{
                svg.transition().call(zoom.scaleBy, 0.75);
            }});
            
            document.getElementById("btnReset").addEventListener("click", () => {{
                svg.transition().call(zoom.transform, d3.zoomIdentity);
            }});
            
            document.getElementById("btnToggleQueries").addEventListener("click", () => {{
                const currentDisplay = node.filter(d => d.type === "query").style("display");
                node.filter(d => d.type === "query")
                    .style("display", currentDisplay === "none" ? "inline" : "none");
                text.filter(d => d.type === "query")
                    .style("display", currentDisplay === "none" ? "inline" : "none");
            }});
            
            document.getElementById("btnToggleLearnings").addEventListener("click", () => {{
                const currentDisplay = node.filter(d => d.type === "learning").style("display");
                node.filter(d => d.type === "learning")
                    .style("display", currentDisplay === "none" ? "inline" : "none");
                text.filter(d => d.type === "learning")
                    .style("display", currentDisplay === "none" ? "inline" : "none");
            }});
            
            document.getElementById("btnToggleSources").addEventListener("click", () => {{
                const currentDisplay = node.filter(d => d.type === "source").style("display");
                node.filter(d => d.type === "source")
                    .style("display", currentDisplay === "none" ? "inline" : "none");
                text.filter(d => d.type === "source")
                    .style("display", currentDisplay === "none" ? "inline" : "none");
            }});
        </script>
    </body>
    </html>
    """
    
    # Sauvegarder le fichier HTML
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    graph_path = REPORTS_DIR / f"knowledge_graph_{timestamp}.html"
    
    try:
        with open(graph_path, "w", encoding="utf-8") as f:
            f.write(html)
        return str(graph_path)
    except Exception as e:
        console.print(f"[{THEME['error_color']}]Erreur lors de la création du graphique de connaissances: {e}[/{THEME['error_color']}]")
        return None

# Composants d'interface
def build_tree(node):
    """Construit un arbre de recherche visuel avec couleurs thématiques"""
    query = node.get('query', TRANSLATION['loading'])
    status = node.get('status', 'waiting')
    
    # Sélectionner la couleur en fonction du statut
    if status == 'completed':
        status_color = THEME['status_completed']
    elif status == 'in_progress':
        status_color = THEME['status_in_progress']
    else:
        status_color = THEME['status_waiting']
    
    # Créer le nœud racine
    tree = Tree(f"[bold {THEME['query_color']}]{query}[/] - [{status_color}]{status}[/]")
    
    def add_nodes(n, parent):
        for child in n.get("sub_queries", []):
            child_query = child.get('query', TRANSLATION['loading'])
            child_status = child.get('status', 'waiting')
            
            # Déterminer la couleur du statut de l'enfant
            if child_status == 'completed':
                child_status_color = THEME['status_completed']
            elif child_status == 'in_progress':
                child_status_color = THEME['status_in_progress']
            else:
                child_status_color = THEME['status_waiting']
            
            # Ajouter le nœud enfant avec formatage
            branch = parent.add(f"[{THEME['info_color']}]{child_query}[/] - [{child_status_color}]{child_status}[/]")
            
            # Ajouter récursivement les enfants de ce nœud
            add_nodes(child, branch)
    
    # Ajouter tous les nœuds enfants
    add_nodes(node, tree)
    return tree

def display_tree(tree_data):
    """Affiche l'arbre de recherche dans un panneau stylisé"""
    if not tree_data:
        return Panel(
            f"[{THEME['warning_color']}]{TRANSLATION['no_tree']}[/{THEME['warning_color']}]",
            title=f"[bold {THEME['info_color']}]{TRANSLATION['research_structure']}[/]",
            border_style=THEME['tree_border'],
            box=THEME['box_style']
        )
    
    tree = build_tree(tree_data)
    return Panel(
        tree,
        title=f"[bold {THEME['info_color']}]{TRANSLATION['research_structure']}[/]",
        border_style=THEME['tree_border'],
        box=THEME['box_style'],
        padding=(1, 2)
    )

def count_nodes(node):
    """Compte le nombre total de nœuds et de nœuds complétés"""
    total = 1
    completed = 1 if node.get("status") == "completed" else 0
    for child in node.get("sub_queries", []):
        t, c = count_nodes(child)
        total += t
        completed += c
    return total, completed

def count_knowledge_points(node):
    """Compte le nombre total de points de connaissance"""
    total = len(node.get("learnings", []))
    for child in node.get("sub_queries", []):
        total += count_knowledge_points(child)
    return total

def extract_unique_sources(visited_urls):
    """Extrait le nombre de sources uniques"""
    return len(visited_urls) if visited_urls else 0

def display_dashboard(tree_data, visited_urls, start_time):
    """Affiche un tableau de bord complet avec statistiques"""
    if not tree_data:
        return Panel(
            f"[{THEME['warning_color']}]{TRANSLATION['no_tree']}[/{THEME['warning_color']}]",
            title=f"[bold {THEME['info_color']}]{TRANSLATION['dashboard']}[/]",
            border_style=THEME['dashboard_border'],
            box=THEME['box_style']
        )
    
    total, completed = count_nodes(tree_data)
    knowledge_points = count_knowledge_points(tree_data)
    current_depth = tree_data.get("depth", 0)
    sources_count = extract_unique_sources(visited_urls)
    elapsed = format_elapsed_time(time.time() - start_time)
    
    # Créer un tableau de statistiques
    stats_table = Table(box=THEME['box_style'], show_header=False, padding=(0, 1))
    stats_table.add_column("Metric", style=f"bold {THEME['info_color']}")
    stats_table.add_column("Value", style="white")
    
    stats_table.add_row(TRANSLATION['total_queries'], str(total))
    stats_table.add_row(TRANSLATION['completed_queries'], f"{completed} ({completed * 100 // total if total > 0 else 0}%)")
    stats_table.add_row(TRANSLATION['research_depth'], str(current_depth))
    stats_table.add_row(TRANSLATION['sources_found'], str(sources_count))
    stats_table.add_row(TRANSLATION['knowledge_points'], str(knowledge_points))
    stats_table.add_row(TRANSLATION['elapsed_time'], elapsed)
    
    # Calcul du ratio de progression
    progress_ratio = completed / total if total > 0 else 0
    
    # Barre de progression visuelle
    progress_bar = "█" * int(progress_ratio * 20) + "░" * (20 - int(progress_ratio * 20))
    progress_text = Text(f"{progress_bar} {progress_ratio * 100:.1f}%")
    
    # État de la recherche
    if completed == total:
        status = Text(f"✓ {TRANSLATION['search_status']}: ", style=THEME['success_color'])
        status.append("COMPLÉTÉ", style=f"bold {THEME['success_color']}")
    else:
        status = Text(f"⟳ {TRANSLATION['search_status']}: ", style=THEME['warning_color'])
        status.append("EN COURS", style=f"bold {THEME['warning_color']}")
    
    # Assembler les composants
    dashboard_content = Group(
        stats_table,
        Text(""),  # Espacement
        status,
        Text(""),  # Espacement
        progress_text
    )
    
    return Panel(
        dashboard_content,
        title=f"[bold {THEME['info_color']}]{TRANSLATION['dashboard']}[/]",
        border_style=THEME['dashboard_border'],
        box=THEME['box_style']
    )

def header_panel():
    """Crée un panneau d'en-tête stylisé"""
    # Version et date
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    version_text = f"v{APP_VERSION} | {now}"
    
    # Créer le titre stylisé
    title = Text(TRANSLATION["app_title"], style=f"bold {THEME['header_fg']} on {THEME['header_bg']}")
    title.justify = "center"
    
    # Ajouter une note de bienvenue
    welcome = Text(f"\n{TRANSLATION['welcome']}", style="italic")
    welcome.justify = "center"
    
    # Ajouter la version en bas
    footer = Text(f"\n{version_text}", style="dim")
    footer.justify = "right"
    
    # Assembler le contenu
    header_content = Group(title, welcome, footer)
    
    return Panel(
        header_content,
        border_style=THEME['header_border'],
        box=THEME['box_style'],
        padding=(1, 2)
    )

def help_panel():
    """Crée un panneau d'aide contextuelle"""
    # Infos sur les modes de recherche
    modes_table = Table(box=None, show_header=False, padding=(0, 1))
    modes_table.add_column("Mode", style=f"bold {THEME['info_color']}")
    modes_table.add_column("Description", style="white")
    
    modes_table.add_row("⚡", TRANSLATION['help_mode_fast'])
    modes_table.add_row("⚖️", TRANSLATION['help_mode_balanced'])
    modes_table.add_row("🔍", TRANSLATION['help_mode_comprehensive'])
    
    # Assembler le contenu d'aide
    help_content = Group(
        modes_table
    )
    
    return Panel(
        help_content,
        title="Aide & Information",
        border_style=THEME['help_border'],
        box=THEME['box_style'],
        padding=(1, 2)
    )

def ask_follow_up_questions(ds, initial_query):
    """Interface améliorée pour les questions de suivi"""
    try:
        follow_up_questions = ds.generate_follow_up_questions(initial_query)
    except Exception as e:
        console.print(Panel(
            f"[{THEME['error_color']}]{TRANSLATION['error_questions']}: {e}[/{THEME['error_color']}]",
            border_style=THEME['error_color'],
            box=THEME['box_style']
        ))
        return []
    
    # Afficher un en-tête pour les questions
    if follow_up_questions:
        console.print(Text(f"\n{TRANSLATION['generating_questions']}", style=f"bold {THEME['info_color']}"))
    
    answers = []
    for i, question in enumerate(follow_up_questions, 1):
        # Afficher le numéro de la question
        formatted_question = f"[{i}/{len(follow_up_questions)}] {question}"
        answer = Prompt.ask(f"[bold {THEME['query_color']}]{formatted_question}")
        answers.append({"question": question, "answer": answer})
    
    return answers

def combine_query(initial_query, follow_ups):
    """Combine la requête initiale avec les questions de suivi"""
    qa_text = "\n".join([f"- {item['question']}: {item['answer']}" for item in follow_ups])
    combined = f"Initial query: {initial_query}\n\nFollow up Q&A:\n{qa_text}"
    return combined

def follow_up_notice(mode):
    """Affiche une notification sur les questions de suivi générées par Gemini"""
    if mode == "comprehensive":
        notice = Text(TRANSLATION["follow_up_notice"], style=f"bold {THEME['warning_color']}")
        console.print(Panel(
            Align.center(notice),
            border_style=THEME['warning_color'],
            box=THEME['box_style']
        ))

async def run_research(ds, query, breadth, depth):
    """Exécution de la recherche avec suivi de progression via le fichier research_tree.json"""
    console.print(f"[{THEME['info_color']}]Lancement de la recherche...[/{THEME['info_color']}]")
    
    start_time = time.time()
    
    # Fonction de suivi des mises à jour
    async def update_display():
        while True:
            try:
                # Lire l'arbre de recherche actuel s'il existe
                try:
                    with open("research_tree.json", "r", encoding="utf-8") as f:
                        tree_data = json.load(f)
                    
                    # Calculer la progression
                    total, completed = count_nodes(tree_data)
                    progress_percent = (completed / total) * 100 if total > 0 else 0
                    elapsed = format_elapsed_time(time.time() - start_time)
                    
                    # Nettoyer la console et afficher la progression
                    console.clear()
                    console.print(f"[{THEME['info_color']}]Recherche en cours... {progress_percent:.1f}% terminé[/{THEME['info_color']}]")
                    console.print(f"[{THEME['info_color']}]Temps écoulé : {elapsed}[/{THEME['info_color']}]")
                    console.print(f"[{THEME['info_color']}]Requêtes : {completed}/{total}[/{THEME['info_color']}]")
                    
                    # Afficher l'arbre et le tableau de bord
                    tree_panel = display_tree(tree_data)
                    dashboard_panel = display_dashboard(tree_data, {}, start_time)
                    
                    # Créer un layout pour afficher l'arbre et le tableau de bord côte à côte
                    display_layout = Layout()
                    display_layout.split_row(
                        Layout(tree_panel, name="tree", ratio=3),
                        Layout(dashboard_panel, name="dashboard", ratio=2)
                    )
                    console.print(display_layout)
                    
                except FileNotFoundError:
                    # Fichier tree.json pas encore créé, afficher un message d'attente
                    console.print(f"[{THEME['warning_color']}]Initialisation de la recherche en cours...[/{THEME['warning_color']}]")
                except json.JSONDecodeError:
                    # Fichier tree.json potentiellement en cours d'écriture
                    console.print(f"[{THEME['warning_color']}]Mise à jour des données de recherche...[/{THEME['warning_color']}]")
            except Exception as e:
                # Éviter que des erreurs d'affichage interrompent la recherche
                console.print(f"[{THEME['error_color']}]Erreur d'affichage: {e}[/{THEME['error_color']}]")
            
            # Attendre avant la prochaine mise à jour
            await asyncio.sleep(3)
    
    # Lancer la tâche de mise à jour en arrière-plan
    update_task = asyncio.create_task(update_display())
    
    try:
        # Exécuter la recherche (sans le paramètre progress_callback)
        result = await ds.deep_research(query, breadth, depth, learnings=[], visited_urls={})
        
        # Nettoyer
        update_task.cancel()
        try:
            await update_task
        except asyncio.CancelledError:
            pass
        
        console.clear()
        console.print(f"[{THEME['success_color']}]Recherche terminée avec succès[/{THEME['success_color']}]")
        return result
    except Exception as e:
        # Nettoyer en cas d'erreur
        update_task.cancel()
        try:
            await update_task
        except asyncio.CancelledError:
            pass
        
        console.print(f"[{THEME['error_color']}]Erreur pendant la recherche: {e}[/{THEME['error_color']}]")
        return {"learnings": [], "visited_urls": {}}

# Interface principale
async def show_splash_screen():
    """Affiche un écran de démarrage animé"""
    # Texte du logo ASCII
    logo = """
 .d8888b.  8888888888        d8888 8888888b.   .d8888b.  888    888 
d88P       888              d88888 888   Y88b d88P  Y88b 888    888 
Y88b.      888             d88P888 888    888 888    888 888    888 
 "Y888b.   8888888        d88P 888 888   d88P 888        8888888888 
    "Y88b. 888           d88P  888 8888888P"  888        888    888 
      "888 888          d88P   888 888 T88b   888    888 888    888 
Y88b  d88P 888         d8888888888 888  T88b  Y88b  d88P 888    888 
 "Y8888P"  8888888888 d88P     888 888   T88b  "Y8888P"  888    888 
                                                                    
                                                                    
                                                                    
    888                       d8888               888888b.                  
    888                      d88888               888  "88b                 
    888                     d88P888               888  .88P                 
    888                    d88P 888               8888888K.                 
    888                   d88P  888               888  "Y88b                
    888                  d88P   888               888    888                
    888                 d8888888888               888   d88P                
    88888888           d88P     888               8888888P"
    """
    
    # Couleurs pour l'animation
    colors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
    
    # Animation du logo
    for i in range(6):
        console.clear()
        colored_logo = f"[bold {colors[i]}]{logo}[/]"
        console.print(colored_logo)
        console.print(f"\n[bold white]Laboratoire de Recherche Avancée[/]")
        console.print(f"[dim]v{APP_VERSION} | Initialisation...[/]")
        
        # Points de progression
        dots = "." * (i % 4)
        console.print(f"\n[bold cyan]Démarrage{dots.ljust(3)}[/]")
        
        await asyncio.sleep(0.3)
    
    console.clear()

async def main():
    """Interface principale du laboratoire de recherche"""
    # Initialisation
    ensure_dirs()
    load_dotenv()
    
    # Afficher l'écran de démarrage
    await show_splash_screen()
    
    # Mise en page principale
    console.clear()
    layout = Layout()
    layout.split_column(
        Layout(header_panel(), name="header", size=6),
        Layout(name="main")
    )
    
    layout["main"].split_row(
        Layout(name="left", ratio=3),
        Layout(help_panel(), name="right", ratio=1)
    )
    
    console.print(layout)
    
    # Collecter les informations pour la recherche
    initial_query = Prompt.ask(f"[bold {THEME['query_color']}]{TRANSLATION['enter_query']}")
    mode = Prompt.ask(
        f"[bold {THEME['info_color']}]{TRANSLATION['select_mode']}",
        choices=["fast", "balanced", "comprehensive"],
        default="comprehensive"
    )
    breadth = int(Prompt.ask(
        f"[bold {THEME['info_color']}]{TRANSLATION['select_breadth']}",
        default="10"
    ))
    depth = int(Prompt.ask(
        f"[bold {THEME['info_color']}]{TRANSLATION['select_depth']}",
        default="5"
    ))
    
    # Initialiser DeepSearch
    ds = DeepSearch(api_key=os.getenv("GEMINI_KEY"), mode=mode)
    
    # Marquer le début de la recherche
    start_time = time.time()
    
    # Générer et poser des questions de suivi
    console.print(Panel(
        f"[{THEME['success_color']}]{TRANSLATION['generating_questions']}[/{THEME['success_color']}]",
        border_style=THEME['info_color'],
        box=THEME['box_style']
    ))
    
    follow_up_answers = ask_follow_up_questions(ds, initial_query)
    
    if follow_up_answers:
        combined_query = combine_query(initial_query, follow_up_answers)
        console.print(Panel(
            f"[{THEME['info_color']}]{TRANSLATION['combined_query']}\n{combined_query}[/{THEME['info_color']}]",
            border_style=THEME['info_color'],
            box=THEME['box_style']
        ))
    else:
        combined_query = initial_query
    
    # Lancer la recherche
    console.print(Panel(
        f"[{THEME['success_color']}]{TRANSLATION['launching_research']}[/{THEME['success_color']}]",
        border_style=THEME['info_color'],
        box=THEME['box_style']
    ))
    
    # Exécuter la recherche
    result = await run_research(ds, combined_query, breadth, depth)
    
    # Lire l'arbre final
    try:
        with open("research_tree.json", "r", encoding="utf-8") as f:
            tree_data = json.load(f)
    except Exception:
        tree_data = {}
    
    # Afficher les résultats de la recherche
    console.clear()
    results_layout = Layout()
    results_layout.split_row(
        Layout(display_tree(tree_data), name="tree", ratio=3),
        Layout(display_dashboard(tree_data, result.get("visited_urls", {}), start_time), name="dashboard", ratio=2)
    )
    
    console.print(results_layout)
    
    # Notification pour les questions de suivi
    follow_up_notice(mode)
    
    # Enregistrer l'arbre de recherche
    if tree_data:
        save_json(tree_data, f"research_tree_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "trees")
    
    # Demander si l'utilisateur souhaite générer un rapport final
    final_choice = Confirm.ask(
        f"[{THEME['info_color']}]{TRANSLATION['generate_report']}[/{THEME['info_color']}]",
        default=True
    )
    
    if final_choice:
        learnings = result.get("learnings", [])
        visited_urls = result.get("visited_urls", {})
        
        console.print(Panel(
            f"[{THEME['success_color']}]{TRANSLATION['generating_report']}[/{THEME['success_color']}]",
            border_style=THEME['info_color'],
            box=THEME['box_style']
        ))
        
        try:
            report = ds.generate_final_report(combined_query, learnings, visited_urls)
            
            # Afficher le rapport
            md_report = Markdown(report)
            console.print(Panel(
                md_report,
                title=f"[bold {THEME['success_color']}]{TRANSLATION['final_report']}[/bold {THEME['success_color']}]",
                border_style=THEME['success_color'],
                box=THEME['box_style']
            ))
            
            # Sauvegarder le rapport
            report_path = save_markdown(report, initial_query)
            if report_path:
                console.print(Panel(
                    f"[{THEME['success_color']}]{TRANSLATION['report_saved']}[/{THEME['success_color']}]\n{report_path}",
                    border_style=THEME['success_color'],
                    box=THEME['box_style']
                ))
                
                # Exporter en HTML et ouvrir dans le navigateur
                open_html = Confirm.ask(
                    f"[{THEME['info_color']}]{TRANSLATION['open_report']}[/{THEME['info_color']}]",
                    default=True
                )
                
                if open_html:
                    html_path = export_html(report_path, initial_query)
                    if html_path:
                        open_file(html_path)
                        # Utiliser Text au lieu de f-string pour éviter les problèmes de formatage
                        success_msg = Text(TRANSLATION["report_browser_opened"])
                        success_msg.stylize(f"bold {THEME['success_color']}")
                        console.print(success_msg)
            
            # Générer et visualiser le graphique de connaissances
            generate_graph = Confirm.ask(
                f"[{THEME['info_color']}]{TRANSLATION['generate_graph']}[/{THEME['info_color']}]",
                default=True
            )
            
            if generate_graph:
                console.print(Panel(
                    f"[{THEME['info_color']}]{TRANSLATION['generating_graph']}[/{THEME['info_color']}]",
                    border_style=THEME['info_color'],
                    box=THEME['box_style']
                ))
                
                # Générer le graphique
                graph_path = generate_knowledge_graph(tree_data, visited_urls)
                
                if graph_path:
                    console.print(f"[{THEME['success_color']}]{TRANSLATION['graph_generated']}: {graph_path}[/{THEME['success_color']}]")
                    
                    # Demander s'il faut ouvrir le graphique dans le navigateur
                    open_graph = Confirm.ask(
                        f"[{THEME['info_color']}]{TRANSLATION['open_graph']}[/{THEME['info_color']}]",
                        default=True
                    )
                    
                    if open_graph:
                        open_file(graph_path)
                        # Utiliser Text au lieu de f-string pour éviter les problèmes de formatage
                        success_msg = Text(TRANSLATION["graph_browser_opened"])
                        success_msg.stylize(f"bold {THEME['success_color']}")
                        console.print(success_msg)
            
        except ResourceExhausted as e:
            console.print(Panel(
                f"[{THEME['error_color']}]{TRANSLATION['error_quota']}\n{e}[/{THEME['error_color']}]",
                border_style=THEME['error_color'],
                box=THEME['box_style']
            ))
        except Exception as e:
            console.print(Panel(
                f"[{THEME['error_color']}]{TRANSLATION['error_report']}: {e}[/{THEME['error_color']}]",
                border_style=THEME['error_color'],
                box=THEME['box_style']
            ))
    else:
        console.print(Panel(
            f"[{THEME['info_color']}]{TRANSLATION['research_completed']}[/{THEME['info_color']}]",
            border_style=THEME['info_color'],
            box=THEME['box_style']
        ))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("[bold red]Recherche interrompue par l'utilisateur.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Erreur inattendue: {e}[/bold red]")
        # Afficher la trace complète en mode développement
        import traceback
        console.print(traceback.format_exc())