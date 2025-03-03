"""
UI Components for Streamlit Interface
Provides reusable UI elements for the application
"""
import streamlit as st
import base64
import json
from pathlib import Path

def display_card(title, content, icon=None, status=None):
    """Display content in a styled card"""
    status_class = ""
    if status == "completed":
        status_class = "status-completed"
    elif status == "in_progress":
        status_class = "status-in-progress"
    
    icon_html = f"<span>{icon}</span> " if icon else ""
    
    st.markdown(f"""
    <div class="card {status_class}">
        <p class="subheader" style="margin-top:0;">{icon_html}{title}</p>
        {content}
    </div>
    """, unsafe_allow_html=True)

def display_metric_row(metrics):
    """
    Display a row of metrics
    
    Args:
        metrics: List of dicts with keys: value, label, color (optional), icon (optional)
    """
    cols = st.columns(len(metrics))
    
    for i, metric in enumerate(metrics):
        color = metric.get('color', 'var(--primary-color)')
        icon = metric.get('icon', '')
        icon_html = f"<span>{icon}</span> " if icon else ""
        
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value" style="color: {color};">{icon_html}{metric['value']}</p>
                <p class="metric-label">{metric['label']}</p>
            </div>
            """, unsafe_allow_html=True)

def display_progress_bar(completed, total, height="10px"):
    """Display a styled progress bar with percentage"""
    if total == 0:
        percent = 0
    else:
        percent = min(100, (completed / total) * 100)  # Cap at 100%
    
    st.markdown(f"""
    <div class="progress-bar-container">
        <div class="progress-bar" style="width: {percent}%; height: {height};"></div>
    </div>
    <p style="margin-top: 5px; text-align: center;">Progress: <span class="highlight-text">{completed}/{total} ({percent:.1f}%)</span></p>
    """, unsafe_allow_html=True)

def display_status_card(title, description, status="in_progress", icon="🔍", progress=None):
    """
    Display a status card with optional progress bar
    
    Args:
        title: Card title
        description: Card description
        status: "in_progress", "completed", "error"
        icon: Emoji icon
        progress: Dict with keys: current, total (optional)
    """
    animation_class = "pulse-animation" if status == "in_progress" else ""
    status_class = f"status-{status}" if status else ""
    
    progress_html = ""
    if progress:
        current = progress.get('current', 0)
        total = progress.get('total', 1)
        percent = min(100, (current / total) * 100) if total > 0 else 0
        
        progress_html = f"""
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: {percent}%;"></div>
        </div>
        <p class="info-text" style="text-align: center;">Progress: {current}/{total} ({percent:.1f}%)</p>
        """
    
    st.markdown(f"""
    <div class="status-card {animation_class} {status_class}">
        <div class="status-icon">{icon}</div>
        <h3>{title}</h3>
        {progress_html}
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)

def display_research_tree_text(tree_data, level=0):
    """Display a simple text-based research tree"""
    if not tree_data:
        return st.write("No research tree data available.")
    
    # Root node
    status_class = "status-completed" if tree_data.get("status") == "completed" else "status-in-progress"
    node_class = f"research-tree-node research-tree-node-{tree_data.get('status', 'in_progress')}"
    
    prefix = "&nbsp;" * 4 * level
    emoji = "✅" if tree_data.get("status") == "completed" else "🔄"
    
    st.markdown(f"""
    <div class="{node_class}" style="margin-left: {level * 20}px;">
        <p style="margin-bottom: 5px;">{emoji} <span class="{status_class}"><strong>{tree_data.get("query", "")[:50]}{"..." if len(tree_data.get("query", "")) > 50 else ""}</strong></span></p>
        <p style="margin-top: 0; font-size: 0.85rem;">Status: <span class="{status_class}">{tree_data.get("status", "").upper()}</span> | Depth: {tree_data.get("depth", 0)} | Learnings: {len(tree_data.get("learnings", []))}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Child nodes
    for child in tree_data.get("sub_queries", []):
        display_research_tree_text(child, level + 1)

def display_research_tree_visual(tree_data):
    """Display an interactive visualization of the research tree using D3.js"""
    if not tree_data:
        return st.write("No research tree data available for visualization.")
    
    # Convert tree_data to a JSON string
    tree_json = json.dumps(tree_data)
    
    st.markdown("""
    <div id="research-tree-viz" style="width: 100%; height: 500px; background-color: var(--bg-secondary); border-radius: 8px; padding: 10px; overflow: auto;"></div>
    <script src="https://d3js.org/d3.v5.min.js"></script>
    <script>
    (function() {
        // Function to create a tree visualization
        function createTree(treeData) {
            // Clear previous visualization
            const vizContainer = document.getElementById('research-tree-viz');
            if (!vizContainer) return;
            
            vizContainer.innerHTML = '';
            
            // Set up dimensions
            const width = vizContainer.offsetWidth;
            const height = 500;
            const margin = {top: 20, right: 120, bottom: 20, left: 120};
            
            // Create SVG
            const svg = d3.select("#research-tree-viz")
                .append("svg")
                .attr("width", width)
                .attr("height", height)
                .append("g")
                .attr("transform", `translate(${margin.left},${margin.top})`);
            
            // Create hierarchical data
            const root = d3.hierarchy(treeData);
            
            // Set node size and layout - use tree layout
            const treeLayout = d3.tree()
                .size([height - margin.top - margin.bottom, width - margin.left - margin.right - 60]);
            
            // Compute the tree layout
            treeLayout(root);
            
            // Add links
            svg.selectAll(".link")
                .data(root.links())
                .enter()
                .append("path")
                .attr("class", "link")
                .attr("d", d => {
                    return `M${d.source.y},${d.source.x}C${(d.source.y + d.target.y) / 2},${d.source.x} ${(d.source.y + d.target.y) / 2},${d.target.x} ${d.target.y},${d.target.x}`;
                })
                .style("fill", "none")
                .style("stroke", "#aaa")
                .style("stroke-width", "2px");
            
            // Add nodes
            const nodes = svg.selectAll(".node")
                .data(root.descendants())
                .enter()
                .append("g")
                .attr("class", d => `node ${d.children ? "node--internal" : "node--leaf"}`)
                .attr("transform", d => `translate(${d.y},${d.x})`);
            
            // Add circles to nodes
            nodes.append("circle")
                .attr("r", 8)
                .style("fill", d => d.data.status === "completed" ? "#28a745" : "#ffc107")
                .style("stroke", "#fff")
                .style("stroke-width", "2px");
            
            // Add labels to nodes
            nodes.append("text")
                .attr("dy", ".31em")
                .attr("x", d => d.children ? -10 : 10)
                .attr("y", 0)
                .attr("text-anchor", d => d.children ? "end" : "start")
                .text(d => {
                    // Truncate long queries
                    const query = d.data.query;
                    if (!query) return "No query";
                    return query.length > 30 ? query.substring(0, 30) + "..." : query;
                })
                .style("font-size", "12px")
                .style("fill", "#333");
            
            // Add tooltips with full query text and learning count
            nodes.append("title")
                .text(d => {
                    const learningCount = d.data.learnings ? d.data.learnings.length : 0;
                    return `${d.data.query || "No query"}\n\nStatus: ${d.data.status || "unknown"}\nLearnings: ${learningCount}\nDepth: ${d.data.depth || "unknown"}`;
                });
        }
        
        // Wait for DOM to load fully
        function checkForContainer() {
            if (document.getElementById('research-tree-viz')) {
                try {
                    // Parse the JSON data
                    const treeData = JSON.parse('TREE_DATA_PLACEHOLDER');
                    createTree(treeData);
                } catch (e) {
                    console.error("Error creating tree visualization:", e);
                    document.getElementById('research-tree-viz').innerHTML = 
                        '<div style="padding: 20px; text-align: center;">Error loading tree visualization</div>';
                }
            } else {
                setTimeout(checkForContainer, 100);
            }
        }
        
        // Start checking for container
        checkForContainer();
    })();
    </script>
    """.replace('TREE_DATA_PLACEHOLDER', tree_json.replace("'", "\\'")), unsafe_allow_html=True)

def create_download_button(file_path, button_text="Download File", file_label='File'):
    """Create a styled download button for a file"""
    if not Path(file_path).exists():
        return st.warning(f"File not found: {file_path}")
    
    with open(file_path, 'rb') as f:
        data = f.read()
    
    b64 = base64.b64encode(data).decode()
    button_uuid = f'download-button-{base64.b64encode(Path(file_path).name.encode()).decode()}'
    
    download_html = f'''
    <a href="data:file/txt;base64,{b64}" id="{button_uuid}" 
       download="{Path(file_path).name}" 
       style="text-decoration: none; display: inline-block; margin: 0 auto;">
        <button class="custom-button">
            {button_text}
        </button>
    </a>
    '''
    
    return download_html

def display_fancy_header(title, subtitle=None, animation_class="fadeIn"):
    """Display a styled header with optional subtitle and animation"""
    subtitle_html = f'<p class="subheader" style="margin-top: -15px;">{subtitle}</p>' if subtitle else ''
    
    st.markdown(f"""
    <div class="{animation_class}" style="text-align: center; margin-bottom: 30px;">
        <h1 class="main-header">{title}</h1>
        {subtitle_html}
        <div class="fancy-divider" style="width: 150px; margin: 20px auto;"></div>
    </div>
    """, unsafe_allow_html=True)

def display_info_box(content, type="info"):
    """
    Display an information box with different styles based on type
    
    Args:
        content: Text content to display
        type: "info", "success", "warning", "error"
    """
    icon_map = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌"
    }
    
    color_map = {
        "info": "var(--primary-color)",
        "success": "var(--success-color)",
        "warning": "var(--warning-color)",
        "error": "var(--danger-color)"
    }
    
    bg_color = f"{color_map.get(type, 'var(--primary-color)')}19"  # 10% opacity
    border_color = color_map.get(type, "var(--primary-color)")
    icon = icon_map.get(type, "ℹ️")
    
    st.markdown(f"""
    <div style="background-color: {bg_color}; border-left: 4px solid {border_color}; padding: 15px; border-radius: var(--border-radius-md); margin: 15px 0;">
        <p style="margin:0;"><strong>{icon} {type.capitalize()}:</strong> {content}</p>
    </div>
    """, unsafe_allow_html=True)

def create_sidebar_section(title, content, icon=None, expanded=True):
    """Create a styled sidebar section with optional icon and expansion"""
    icon_html = f"{icon} " if icon else ""
    
    with st.sidebar:
        with st.expander(f"{icon_html}{title}", expanded=expanded):
            st.markdown(content, unsafe_allow_html=True)

def display_tab_content(tabs_data):
    """
    Display content in styled tabs
    
    Args:
        tabs_data: List of dicts with keys: label, content, icon (optional)
    """
    # Use Streamlit's native tabs
    tab_labels = [f"{tab.get('icon', '')} {tab['label']}" for tab in tabs_data]
    tabs = st.tabs(tab_labels)
    
    for i, tab in enumerate(tabs):
        with tab:
            st.markdown(tabs_data[i]['content'], unsafe_allow_html=True)

def display_timeline(events):
    """
    Display a vertical timeline of events
    
    Args:
        events: List of dicts with keys: title, description, time, status (optional), icon (optional)
    """
    timeline_html = ""
    
    for event in events:
        icon = event.get('icon', '🔵')
        status = event.get('status', '')
        status_class = f"status-{status}" if status else ""
        
        timeline_html += f"""
        <div class="timeline-item">
            <div class="timeline-icon">{icon}</div>
            <div class="timeline-content {status_class}">
                <h4 class="timeline-title">{event['title']}</h4>
                <p class="timeline-time">{event['time']}</p>
                <p class="timeline-description">{event['description']}</p>
            </div>
        </div>
        """
    
    st.markdown(f"""
    <style>
    .timeline-container {{
        position: relative;
        margin: 20px 0;
        padding-left: 40px;
    }}
    .timeline-container:before {{
        content: '';
        position: absolute;
        top: 0;
        left: 15px;
        height: 100%;
        width: 2px;
        background: var(--border-color);
    }}
    .timeline-item {{
        position: relative;
        margin-bottom: 20px;
    }}
    .timeline-icon {{
        position: absolute;
        left: -40px;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background-color: var(--bg-secondary);
        border: 2px solid var(--primary-color);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1;
    }}
    .timeline-content {{
        background: var(--bg-secondary);
        padding: 15px;
        border-radius: var(--border-radius-md);
        box-shadow: var(--shadow-sm);
        border-left: 4px solid var(--primary-color);
        margin-left: 15px;
    }}
    .timeline-title {{
        margin-top: 0;
        margin-bottom: 5px;
        color: var(--text-color);
    }}
    .timeline-time {{
        color: var(--text-secondary);
        font-size: var(--font-size-xs);
        margin-top: 0;
        margin-bottom: 10px;
    }}
    .timeline-content.status-completed {{
        border-left-color: var(--success-color);
    }}
    .timeline-content.status-in-progress {{
        border-left-color: var(--warning-color);
    }}
    .timeline-content.status-error {{
        border-left-color: var(--danger-color);
    }}
    </style>
    <div class="timeline-container">
        {timeline_html}
    </div>
    """, unsafe_allow_html=True)

def display_expandable_sections(sections):
    """
    Display multiple expandable sections
    
    Args:
        sections: List of dicts with keys: title, content, expanded (optional), icon (optional)
    """
    for section in sections:
        icon = section.get('icon', '')
        expanded = section.get('expanded', False)
        
        with st.expander(f"{icon} {section['title']}", expanded=expanded):
            st.markdown(section['content'], unsafe_allow_html=True)

def display_animated_counter(value, label, prefix="", suffix="", animation_duration=2000):
    """
    Display a counter with animation effect
    
    Args:
        value: The final value to count up to
        label: Text label
        prefix: Optional prefix before the number (e.g., "$")
        suffix: Optional suffix after the number (e.g., "%")
        animation_duration: Duration of the counting animation in milliseconds
    """
    counter_id = f"counter-{hash(label)}-{hash(value)}"
    
    st.markdown(f"""
    <div class="animated-counter" id="{counter_id}">
        <div class="counter-value">{prefix}<span class="count">{value}</span>{suffix}</div>
        <div class="counter-label">{label}</div>
    </div>
    
    <script>
    (function() {{
        function animateCounter(counterId) {{
            const counterElement = document.getElementById(counterId);
            if (!counterElement) return;
            
            const countElement = counterElement.querySelector('.count');
            const finalValue = {value};
            const duration = {animation_duration};
            const startTime = performance.now();
            
            const updateCount = (currentTime) => {{
                const elapsedTime = currentTime - startTime;
                const progress = Math.min(elapsedTime / duration, 1);
                const currentCount = Math.floor(progress * finalValue);
                
                countElement.textContent = currentCount;
                
                if (progress < 1) {{
                    requestAnimationFrame(updateCount);
                }} else {{
                    countElement.textContent = finalValue;
                }}
            }};
            
            requestAnimationFrame(updateCount);
        }}
        
        function initCounters() {{
            const observer = new IntersectionObserver((entries) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        animateCounter(entry.target.id);
                        observer.unobserve(entry.target);
                    }}
                }});
            }}, {{ threshold: 0.1 }});
            
            const counterElement = document.getElementById('{counter_id}');
            if (counterElement) observer.observe(counterElement);
        }}
        
        // Check for the element when the DOM is fully loaded
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', initCounters);
        }} else {{
            initCounters();
        }}
    }})();
    </script>
    
    <style>
    .animated-counter {{
        text-align: center;
        padding: 15px;
        background-color: var(--bg-secondary);
        border-radius: var(--border-radius-md);
        margin: 10px 0;
        transition: var(--transition-normal);
        box-shadow: var(--shadow-sm);
    }}
    .animated-counter:hover {{
        transform: translateY(-3px);
        box-shadow: var(--shadow-md);
    }}
    .counter-value {{
        font-size: var(--font-size-xl);
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 5px;
    }}
    .counter-label {{
        font-size: var(--font-size-sm);
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    </style>
    """, unsafe_allow_html=True)

def calculate_tree_stats(tree_data):
    """
    Calculate statistics from a research tree
    
    Args:
        tree_data: Research tree data structure
        
    Returns:
        dict: Statistics about the tree
    """
    stats = {
        "total_nodes": 0,
        "completed": 0,
        "total_learnings": 0,
        "by_depth": {}
    }
    
    def count_nodes(node, stats):
        if not node:
            return
            
        stats["total_nodes"] += 1
        
        depth = node.get("depth", 0)
        if depth not in stats["by_depth"]:
            stats["by_depth"][depth] = {"total": 0, "completed": 0, "learnings": 0}
            
        stats["by_depth"][depth]["total"] += 1
        
        if node.get("status") == "completed":
            stats["completed"] += 1
            stats["by_depth"][depth]["completed"] += 1
            
        learnings = len(node.get("learnings", []))
        stats["total_learnings"] += learnings
        stats["by_depth"][depth]["learnings"] += learnings
        
        for sub_query in node.get("sub_queries", []):
            count_nodes(sub_query, stats)
    
    count_nodes(tree_data, stats)
    return stats