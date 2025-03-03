import streamlit as st
import asyncio
import os
import time
import json
import base64
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

from src.deep_research import DeepSearch
from src.export_utils import ExportUtils  # Import the new export utilities

# Load environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="Open Gemini Deep Research",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #4b6fff;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .subheader {
        font-size: 1.5rem;
        color: #6c757d;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .card {
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        background-color: #f8f9fa;
        border-left: 5px solid #4b6fff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .info-text {
        font-size: 0.9rem;
        color: #6c757d;
    }
    .status-completed {
        color: #28a745;
        font-weight: bold;
    }
    .status-in-progress {
        color: #ffc107;
        font-weight: bold;
    }
    .research-tree-node {
        margin-left: 20px;
        padding: 10px;
        border-left: 3px solid #4b6fff;
        margin-bottom: 10px;
        transition: all 0.3s ease;
    }
    .research-tree-node:hover {
        background-color: rgba(75, 111, 255, 0.05);
    }
    .research-tree-node-completed {
        border-left: 3px solid #28a745;
    }
    .research-tree-node-in-progress {
        border-left: 3px solid #ffc107;
    }
    .progress-bar-container {
        width: 100%;
        background-color: #e9ecef;
        border-radius: 5px;
        margin: 10px 0;
        overflow: hidden;
    }
    .progress-bar {
        height: 10px;
        border-radius: 5px;
        background-color: #4b6fff;
        transition: width 0.5s ease;
    }
    .status-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #dee2e6;
    }
    .status-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    .highlight-text {
        background-color: #e9f2ff;
        padding: 2px 5px;
        border-radius: 3px;
        font-weight: 500;
    }
    .metric-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #e9ecef;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #4b6fff;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .rich-tree-node {
        background-color: white;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #4b6fff;
        transition: all 0.3s ease;
    }
    .rich-tree-node:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .rich-tree-node-completed {
        border-left: 5px solid #28a745;
    }
    .rich-tree-node-in-progress {
        border-left: 5px solid #ffc107;
    }
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(75, 111, 255, 0.7);
        }
        70% {
            box-shadow: 0 0 0 10px rgba(75, 111, 255, 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(75, 111, 255, 0);
        }
    }
    .fancy-divider {
        height: 3px;
        background: linear-gradient(90deg, rgba(75, 111, 255, 0) 0%, rgba(75, 111, 255, 1) 50%, rgba(75, 111, 255, 0) 100%);
        margin: 20px 0;
    }
    table {
        border-collapse: separate !important;
        border-spacing: 0 !important;
    }
    table td, table th {
        border-radius: 0 !important;
    }
    table tr:first-child th:first-child {
        border-top-left-radius: 8px !important;
    }
    table tr:first-child th:last-child {
        border-top-right-radius: 8px !important;
    }
    table tr:last-child td:first-child {
        border-bottom-left-radius: 8px !important;
    }
    table tr:last-child td:last-child {
        border-bottom-right-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to display research tree visualization
def display_research_tree(tree_data):
    if not tree_data:
        return
    
    # Convert the tree to a graph visualization using d3.js
    st.markdown("""
    <div id="research-tree-viz" style="width: 100%; height: 500px;"></div>
    <script src="https://d3js.org/d3.v5.min.js"></script>
    <script>
        function visualizeTree(treeData) {
            // Clear previous visualization
            d3.select("#research-tree-viz").selectAll("*").remove();
            
            // Set up dimensions
            const width = document.getElementById('research-tree-viz').offsetWidth;
            const height = 500;
            const margin = {top: 20, right: 90, bottom: 20, left: 90};
            
            // Create SVG
            const svg = d3.select("#research-tree-viz")
                .append("svg")
                .attr("width", width)
                .attr("height", height)
                .append("g")
                .attr("transform", `translate(${margin.left},${margin.top})`);
            
            // Create hierarchical data
            const root = d3.hierarchy(treeData);
            
            // Set node size and layout
            const treeLayout = d3.tree()
                .size([height - margin.top - margin.bottom, width - margin.left - margin.right]);
            
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
                .style("stroke", "#ccc")
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
                .attr("r", 6)
                .style("fill", d => d.data.status === "completed" ? "#28a745" : "#ffc107")
                .style("stroke", "#fff")
                .style("stroke-width", "2px");
            
            // Add labels to nodes
            nodes.append("text")
                .attr("dy", ".31em")
                .attr("x", d => d.children ? -8 : 8)
                .attr("text-anchor", d => d.children ? "end" : "start")
                .text(d => {
                    // Truncate long queries
                    const query = d.data.query;
                    return query.length > 30 ? query.substring(0, 30) + "..." : query;
                })
                .style("font-size", "12px");
            
            // Add tooltips with full query text and learning count
            nodes.append("title")
                .text(d => {
                    const learningCount = d.data.learnings ? d.data.learnings.length : 0;
                    return `${d.data.query}\n\nStatus: ${d.data.status}\nLearnings: ${learningCount}\nDepth: ${d.data.depth}`;
                });
        }
        
        // Call the visualization with the data
        visualizeTree(${json.dumps(tree_data)});
    </script>
    """, unsafe_allow_html=True)

# Function to display a simple text-based research tree
def display_text_tree(tree_data, level=0):
    if not tree_data:
        return st.write("No research tree data available.")
    
    # Root node
    status_class = "status-completed" if tree_data["status"] == "completed" else "status-in-progress"
    node_class = f"rich-tree-node rich-tree-node-{tree_data['status']}"
    
    if level == 0:
        st.markdown(f"""
        <div class="{node_class}">
            <h4>📊 Root Query: <span class="{status_class}">{tree_data["query"][:50]}{"..." if len(tree_data["query"]) > 50 else ""}</span></h4>
            <p>Status: <span class="{status_class}">{tree_data["status"].upper()}</span> | Depth: {tree_data["depth"]} | Learnings: {len(tree_data["learnings"])}</p>
            <p class="info-text">This is the main research query that initiated the research process.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        prefix = "&nbsp;" * 4 * level
        emoji = "✅" if tree_data["status"] == "completed" else "🔄"
        st.markdown(f"""
        <div class="{node_class}" style="margin-left: {level * 20}px;">
            <p>{prefix} {emoji} <span class="{status_class}">{tree_data["query"][:50]}{"..." if len(tree_data["query"]) > 50 else ""}</span></p>
            <p>{prefix} Status: <span class="{status_class}">{tree_data["status"].upper()}</span> | Depth: {tree_data["depth"]} | Learnings: {len(tree_data["learnings"])}</p>
            {f'<p class="info-text">{prefix} Found {len(tree_data["learnings"])} key insights from this query branch.</p>' if tree_data["learnings"] else ''}
        </div>
        """, unsafe_allow_html=True)
    
    # Child nodes
    for child in tree_data["sub_queries"]:
        display_text_tree(child, level + 1)

# Function to display progress bar
def display_progress_bar(completed, total):
    if total == 0:
        percent = 0
    else:
        percent = (completed / total) * 100
    
    st.markdown(f"""
    <div class="progress-bar-container">
        <div class="progress-bar" style="width: {percent}%"></div>
    </div>
    <p>Progress: <span class="highlight-text">{completed}/{total} queries completed ({percent:.1f}%)</span></p>
    """, unsafe_allow_html=True)

# Function to download a file
def get_binary_file_downloader_html(file_path, file_label='File', button_text="Download File"):
    with open(file_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    button_uuid = f'download-button-{base64.b64encode(os.path.basename(file_path).encode()).decode()}'
    button_html = f'''
        <a href="data:file/txt;base64,{b64}" id="{button_uuid}" 
           download="{os.path.basename(file_path)}" 
           style="text-decoration: none; color: white;">
            <button style="background-color: #4CAF50; color: white; padding: 8px 16px;
                    border: none; border-radius: 4px; cursor: pointer;">
                {button_text}
            </button>
        </a>
    '''
    return button_html

# Function to calculate research tree statistics
def calculate_tree_stats(tree_data):
    if not tree_data:
        return {"total_nodes": 0, "completed": 0, "in_progress": 0, "total_learnings": 0, "by_depth": {}}
    
    stats = {"total_nodes": 0, "completed": 0, "in_progress": 0, "total_learnings": 0, "by_depth": {}}
    
    def traverse_tree(node, depth=0):
        # Initialize depth stats if needed
        if depth not in stats["by_depth"]:
            stats["by_depth"][depth] = {"total": 0, "completed": 0, "learnings": 0}
        
        # Update stats
        stats["total_nodes"] += 1
        stats["by_depth"][depth]["total"] += 1
        stats["total_learnings"] += len(node["learnings"])
        stats["by_depth"][depth]["learnings"] += len(node["learnings"])
        
        if node["status"] == "completed":
            stats["completed"] += 1
            stats["by_depth"][depth]["completed"] += 1
        else:
            stats["in_progress"] += 1
        
        # Recurse for child nodes
        for child in node["sub_queries"]:
            traverse_tree(child, depth + 1)
    
    traverse_tree(tree_data)
    return stats

# Function to run in a separate thread
async def run_deep_research(query, mode, api_key, follow_up_answers=None, status_placeholder=None):
    if status_placeholder:
        status_placeholder.markdown(f"""
        <div class="status-card pulse-animation">
            <div class="status-icon">🔍</div>
            <h3>Initializing Research</h3>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: 5%"></div>
            </div>
            <p>Setting up research environment for: <span class="highlight-text">{query[:50]}{"..." if len(query) > 50 else ""}</span></p>
            <p class="info-text">Preparing to analyze query complexity and structure research approach...</p>
        </div>
        """, unsafe_allow_html=True)
    
    deep_search = DeepSearch(api_key, mode=mode)
    
    # Determine research breadth and depth
    if status_placeholder:
        status_placeholder.markdown(f"""
        <div class="status-card pulse-animation">
            <div class="status-icon">📊</div>
            <h3>Analyzing Query Complexity</h3>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: 15%"></div>
            </div>
            <p>Determining optimal research breadth and depth for: <span class="highlight-text">{query[:50]}{"..." if len(query) > 50 else ""}</span></p>
            <p class="info-text">Just like in the CLI version, this step evaluates how wide and deep the research should go based on query complexity.</p>
        </div>
        """, unsafe_allow_html=True)
    
    breadth_and_depth = deep_search.determine_research_breadth_and_depth(query)
    breadth = breadth_and_depth["breadth"]
    depth = breadth_and_depth["depth"]
    
    if status_placeholder:
        status_placeholder.markdown(f"""
        <div class="status-card">
            <div class="status-icon">📐</div>
            <h3>Analysis Complete</h3>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: 20%"></div>
            </div>
            <p>
                <div class="metric-card" style="display: inline-block; margin-right: 10px; width: 45%;">
                    <div class="metric-value">{breadth}/10</div>
                    <div class="metric-label">Research Breadth</div>
                </div>
                <div class="metric-card" style="display: inline-block; width: 45%;">
                    <div class="metric-value">{depth}/5</div>
                    <div class="metric-label">Research Depth</div>
                </div>
            </p>
            <p class="highlight-text">{breadth_and_depth["explanation"].split('.')[0]}.</p>
            <p class="info-text">{'.'.join(breadth_and_depth["explanation"].split('.')[1:])}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Small delay to show the analysis results
        await asyncio.sleep(2)
    
    # Combine query with follow-up answers if provided
    if follow_up_answers:
        questions_and_answers = "\n".join([
            f"{q}: {a}" for q, a in follow_up_answers.items() if a
        ])
        combined_query = f"Initial query: {query}\n\n Follow up questions and answers: {questions_and_answers}"
    else:
        combined_query = query
    
    # Run the deep research
    if status_placeholder:
        status_placeholder.markdown(f"""
        <div class="status-card pulse-animation">
            <div class="status-icon">🚀</div>
            <h3>Running Deep Research</h3>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: 30%"></div>
            </div>
            <p>Research configuration:</p>
            <ul>
                <li><strong>Mode:</strong> {mode.capitalize()}</li>
                <li><strong>Breadth:</strong> {breadth}/10</li>
                <li><strong>Depth:</strong> {depth}/5</li>
            </ul>
            <p class="info-text">Researching multiple sources, generating queries, and extracting insights. This process has multiple stages and may take several minutes based on the selected research mode.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Wait a bit before showing the next status update
        await asyncio.sleep(3) 
        
        status_placeholder.markdown(f"""
        <div class="status-card pulse-animation">
            <div class="status-icon">🔎</div>
            <h3>Exploring Research Space</h3>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: 40%"></div>
            </div>
            <p>Currently:</p>
            <ul>
                <li>Generating diverse research queries</li>
                <li>Exploring topic breadth and potential knowledge branches</li>
                <li>Prioritizing research directions</li>
            </ul>
            <p class="info-text">The system is creating a comprehensive research plan based on your query and follow-up answers.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Start the actual research process with a bit of delay to show the UI updates
    await asyncio.sleep(2)
    
    results = await deep_search.deep_research(
        query=combined_query,
        breadth=breadth,
        depth=depth,
        learnings=[],
        visited_urls={}
    )
    
    # Update with intermediate progress once we have initial results
    if status_placeholder:
        status_placeholder.markdown(f"""
        <div class="status-card">
            <div class="status-icon">📑</div>
            <h3>Research in Progress</h3>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: 65%"></div>
            </div>
            <p>Current status:</p>
            <ul>
                <li>Found <span class="highlight-text">{len(results["learnings"])}</span> key insights</li>
                <li>Analyzed <span class="highlight-text">{len(results["visited_urls"])}</span> sources</li>
                <li>Building research tree with multiple branches and depths</li>
            </ul>
            <p class="info-text">Continuing to extract and organize learnings from all research branches...</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Wait a moment before showing next status
    await asyncio.sleep(2)
    
    # Generate the final report
    if status_placeholder:
        status_placeholder.markdown(f"""
        <div class="status-card pulse-animation">
            <div class="status-icon">📝</div>
            <h3>Generating Final Research Report</h3>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: 75%"></div>
            </div>
            <p>Synthesizing <span class="highlight-text">{len(results["learnings"])}</span> findings into a comprehensive report</p>
            <ul>
                <li>Organizing insights by theme and importance</li>
                <li>Connecting related concepts</li>
                <li>Creating citations and references</li>
                <li>Formatting final document</li>
            </ul>
            <p class="info-text">This phase combines all research findings into a structured report with proper citations and formatting.</p>
        </div>
        """, unsafe_allow_html=True)
    
    final_report = deep_search.generate_final_report(
        query=combined_query,
        learnings=results["learnings"],
        visited_urls=results["visited_urls"],
        sanitized_query=results["sanitized_query"]
    )
    
    # Wait a moment before showing completion
    await asyncio.sleep(2)
    
    if status_placeholder:
        status_placeholder.markdown(f"""
        <div class="status-card">
            <div class="status-icon">✅</div>
            <h3>Research Completed!</h3>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: 100%"></div>
            </div>
            <p>Successfully completed research on: <span class="highlight-text">{query[:50]}{"..." if len(query) > 50 else ""}</span></p>
            <p>Results summary:</p>
            <ul>
                <li>Generated <span class="highlight-text">{len(results["learnings"])}</span> key insights</li>
                <li>Analyzed <span class="highlight-text">{len(results["visited_urls"])}</span> different sources</li>
                <li>Created comprehensive research report with citations</li>
                <li>Saved complete research tree for reference</li>
            </ul>
            <p class="info-text">Full research results and detailed report are ready for review.</p>
        </div>
        """, unsafe_allow_html=True)
    
    return {
        "breadth": breadth,
        "depth": depth,
        "explanation": breadth_and_depth["explanation"],
        "learnings": results["learnings"],
        "visited_urls": results["visited_urls"],
        "final_report": final_report,
        "sanitized_query": results["sanitized_query"],
        "research_tree": results.get("research_tree", {})  # Include the research tree structure
    }

# Main app
def main():
    # Sidebar with a fancy header and gradient background
    st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, #4b6fff 0%, #3f5efb 100%); padding: 20px; border-radius: 8px; margin-bottom: 20px; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
        <h2 style="margin:0; padding:0; font-weight:700;">🔍 Open Gemini</h2>
        <h3 style="margin:0; padding:0; font-weight:500;">Deep Research</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # API Key input with better styling
    st.sidebar.markdown('<p style="font-weight: 600; margin-bottom: 5px;">Gemini API Key</p>', unsafe_allow_html=True)
    api_key = st.sidebar.text_input("", type="password", value=os.getenv('GEMINI_KEY', ''), placeholder="Enter your API key here", key="api_key_input")
    if not api_key:
        st.sidebar.warning("⚠️ Please enter your Gemini API Key to continue")
    
    # Research mode selection with icons and better descriptions
    st.sidebar.markdown('<p style="font-weight: 600; margin: 20px 0 5px 0;">Research Mode</p>', unsafe_allow_html=True)
    
    mode_descriptions = {
        "fast": {
            "icon": "🚀",
            "title": "Fast", 
            "desc": "Quick overview with basic insights",
            "time": "1-2 min",
            "detail": "Best for simple topics where you need quick answers"
        },
        "balanced": {
            "icon": "⚖️",
            "title": "Balanced", 
            "desc": "Good balance between speed and depth",
            "time": "3-6 min",
            "detail": "Recommended for most research queries"
        },
        "comprehensive": {
            "icon": "🔬",
            "title": "Comprehensive", 
            "desc": "In-depth research with deeper insights",
            "time": "5-15 min",
            "detail": "Best for complex or specialized topics"
        }
    }
    
    # Create radio buttons for mode selection with rich formatting
    mode = st.sidebar.radio(
        label="",
        options=["fast", "balanced", "comprehensive"],
        index=1,  # Default to balanced
        format_func=lambda x: f"{mode_descriptions[x]['icon']} {mode_descriptions[x]['title']}"
    )
    
    # Show details for selected mode
    st.sidebar.markdown(f"""
    <div style="background-color: rgba(75, 111, 255, 0.1); border-left: 3px solid #4b6fff; padding: 10px; border-radius: 4px;">
        <p style="margin:0; font-weight:600;">{mode_descriptions[mode]['desc']}</p>
        <p style="margin:0; color:#6c757d;"><strong>Time:</strong> {mode_descriptions[mode]['time']}</p>
        <p style="margin:5px 0 0 0; font-size:0.9rem; color:#6c757d;">{mode_descriptions[mode]['detail']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add fancy divider
    st.sidebar.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)
    
    # About section in sidebar with better formatting
    with st.sidebar.expander("ℹ️ About Open Gemini Deep Research"):
        st.markdown("""
        <div style="text-align: center; margin-bottom: 10px;">
            <img src="https://storage.googleapis.com/gweb-uniblog-publish-prod/images/gemini_1.width-1300.format-webp.webp" style="width: 100%; border-radius: 5px; margin-bottom: 10px;">
        </div>
        <p>This tool performs deep research using Google's Gemini AI model. 
        It generates queries, processes search results, extracts learnings, 
        and creates a comprehensive research report.</p>
        
        <h4>Research Modes:</h4>
        <ul>
            <li><strong>Fast:</strong> Quick overview with minimal depth</li>
            <li><strong>Balanced:</strong> Good compromise between speed and detail</li>
            <li><strong>Comprehensive:</strong> Maximum detail and coverage with recursive exploration</li>
        </ul>
        
        <h4>How It Works:</h4>
        <ol>
            <li>Analyzes your query complexity</li>
            <li>Determines optimal research breadth and depth</li>
            <li>Generates follow-up questions to refine understanding</li>
            <li>Creates a research tree to explore the topic</li>
            <li>Recursively explores and learns from each branch</li>
            <li>Synthesizes findings into a comprehensive report</li>
        </ol>
        
        <p style="font-size: 0.8rem; color: #6c757d; text-align: center; margin-top: 20px;">
            Powered by Google Gemini AI and Streamlit
        </p>
        """, unsafe_allow_html=True)
    
    # Main content with fancy header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 class="main-header">🔍 Open Gemini Deep Research</h1>
        <p class="subheader" style="margin-top: -15px;">AI-powered deep research assistant</p>
        <div style="width: 100px; height: 3px; background: linear-gradient(90deg, rgba(75, 111, 255, 0) 0%, rgba(75, 111, 255, 1) 50%, rgba(75, 111, 255, 0) 100%); margin: 0 auto;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Query input with styled container and placeholder
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<p class="subheader" style="margin-top:0;">Research Query</p>', unsafe_allow_html=True)
    st.markdown('<p class="info-text">Enter a specific question or research topic to explore in depth</p>', unsafe_allow_html=True)
    query = st.text_area(
        label="",
        placeholder="Example: What are the potential impacts of quantum computing on cybersecurity?", 
        height=100
    )
    
    # Initialize session state for follow-up questions
    if 'follow_up_questions' not in st.session_state:
        st.session_state.follow_up_questions = []
        
    if 'research_running' not in st.session_state:
        st.session_state.research_running = False
        
    if 'research_results' not in st.session_state:
        st.session_state.research_results = None
        
    if 'follow_up_answered' not in st.session_state:
        st.session_state.follow_up_answered = False
    
    # Start research button with better styling
    col1, col2 = st.columns([1, 5])
    with col1:
        start_disabled = not api_key or not query or st.session_state.research_running
        button_style = "opacity: 0.6;" if start_disabled else ""
        if start_disabled:
            st.markdown(f"""
            <button style="background: linear-gradient(90deg, #4b6fff, #6495ED); color: white; border: none; padding: 10px 20px; border-radius: 5px; font-weight: 600; cursor: not-allowed; {button_style}">
                Start Research
            </button>
            """, unsafe_allow_html=True)
            start_button = False
        else:
            start_button = st.button(
                "Start Research", 
                type="primary",
                use_container_width=True,
            )
    
    with col2:
        if st.session_state.research_running:
            st.markdown("""
            <div style="background-color: rgba(75, 111, 255, 0.1); border-left: 3px solid #4b6fff; padding: 10px; border-radius: 4px;">
                <p style="margin:0;"><strong>⏳ Research in progress...</strong> This process may take several minutes depending on the research mode and topic complexity.</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close the query card
    
    # Generate follow-up questions when Start button is clicked
    if start_button and api_key and query:
        st.session_state.research_running = True
        st.session_state.follow_up_answered = False
        
        # Show a status indicator while generating questions
        status_container = st.empty()
        status_container.markdown("""
        <div class="status-card pulse-animation">
            <div class="status-icon">❓</div>
            <h3>Generating Follow-up Questions</h3>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: 30%"></div>
            </div>
            <p>Analyzing your research query to generate relevant follow-up questions...</p>
            <p class="info-text">This helps the system better understand your research needs and provide more targeted results.</p>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            deep_search = DeepSearch(api_key, mode=mode)
            st.session_state.follow_up_questions = deep_search.generate_follow_up_questions(query)
            status_container.empty()  # Clear the status indicator
        except Exception as e:
            st.error(f"Error generating follow-up questions: {str(e)}")
            st.session_state.research_running = False
    
    # Display follow-up questions if available
    if st.session_state.follow_up_questions and not st.session_state.follow_up_answered:
        st.markdown("""
        <div class="card" style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);">
            <p class="subheader" style="margin-top:0;">Follow-up Questions</p>
            <p>To better understand your research needs, please answer these follow-up questions:</p>
        """, unsafe_allow_html=True)
        
        follow_up_answers = {}
        for i, question in enumerate(st.session_state.follow_up_questions):
            st.markdown(f"""
            <div style="margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #4b6fff;">
                <p style="margin-bottom: 5px; font-weight: 500;">Question {i+1}:</p>
                <p style="margin-top: 0;">{question}</p>
            </div>
            """, unsafe_allow_html=True)
            follow_up_answers[question] = st.text_input(f"Answer {i+1}", key=f"answer_{i}", label_visibility="collapsed")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Continue button with better styling
        col1, col2 = st.columns([1, 5])
        with col1:
            continue_button = st.button("Continue Research", type="primary", use_container_width=True)
        
        with col2:
            st.markdown("""
            <div style="padding: 10px;">
                <p class="info-text" style="margin:0;">These answers will help refine the research approach and focus on aspects most relevant to your needs.</p>
            </div>
            """, unsafe_allow_html=True)
        
        if continue_button:
            st.session_state.follow_up_answered = True
            
            # Create a status placeholder
            status_placeholder = st.empty()
            
            # Start the research process
            try:
                # Run the research asynchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                start_time = time.time()
                results = loop.run_until_complete(run_deep_research(query, mode, api_key, follow_up_answers, status_placeholder))
                elapsed_time = time.time() - start_time
                
                # Store results in session state
                st.session_state.research_results = results
                st.session_state.research_results['elapsed_time'] = elapsed_time
                st.session_state.research_running = False
                
                # Force a rerun to display results
                st.rerun()
            except Exception as e:
                st.error(f"Error during research: {str(e)}")
                st.session_state.research_running = False
    
    # Display research results if available
    if st.session_state.research_results:
        results = st.session_state.research_results
        
        # Show completion banner
        st.markdown(f"""
        <div style="text-align: center; margin: 30px 0;">
            <div style="display: inline-block; background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 15px 40px; border-radius: 50px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="margin:0; padding:0;">✅ Research Complete!</h2>
                <p style="margin:0; padding:0;">Completed in {int(results['elapsed_time'] // 60)} minutes and {int(results['elapsed_time'] % 60)} seconds</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display research parameters with improved styling
        st.markdown("""
        <div class="card">
            <p class="subheader" style="margin-top:0;">Research Parameters</p>
            <p class="info-text">These parameters determined the scope and depth of your research</p>
        """, unsafe_allow_html=True)
        
        # Create 3 columns with metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="height: 100%;">
                <h4 style="margin:0; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.9rem;">Research Breadth</h4>
                <p class="metric-value">{results['breadth']}<span style="font-size: 1rem; color: #6c757d;">/10</span></p>
                <p style="margin:0; font-size: 0.8rem; color: #6c757d;">Determines how many parallel queries are explored</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="height: 100%;">
                <h4 style="margin:0; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.9rem;">Research Depth</h4>
                <p class="metric-value">{results['depth']}<span style="font-size: 1rem; color: #6c757d;">/5</span></p>
                <p style="margin:0; font-size: 0.8rem; color: #6c757d;">Controls how many levels deep the research goes</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            minutes = int(results['elapsed_time'] // 60)
            seconds = int(results['elapsed_time'] % 60)
            st.markdown(f"""
            <div class="metric-card" style="height: 100%;">
                <h4 style="margin:0; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.9rem;">Research Time</h4>
                <p class="metric-value">{minutes}<span style="font-size: 1rem; color: #6c757d;">m</span> {seconds}<span style="font-size: 1rem; color: #6c757d;">s</span></p>
                <p style="margin:0; font-size: 0.8rem; color: #6c757d;">Total time taken to complete the research</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Explanation box
        st.markdown(f"""
        <div style="background-color: rgba(75, 111, 255, 0.1); border-radius: 8px; padding: 15px; margin-top: 15px;">
            <p style="margin:0;"><strong>Complexity Analysis:</strong> {results['explanation']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display research statistics with enhanced visuals
        st.markdown("""
        <div class="card" style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);">
            <p class="subheader" style="margin-top:0;">Research Statistics</p>
            <p class="info-text">Detailed metrics about the research process and structure</p>
        """, unsafe_allow_html=True)
        
        # Try to load the research tree from file
        tree_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "results", 
            f"research_tree_{results['sanitized_query']}.json"
        )
        
        tree_data = None
        if os.path.exists(tree_path):
            with open(tree_path, 'r') as f:
                tree_data = json.load(f)
        elif 'research_tree' in results:
            tree_data = results['research_tree']
            
        if tree_data:
            stats = calculate_tree_stats(tree_data)
            
            # Display tree statistics with enhanced visuals
            st.markdown('<div style="display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 20px;">', unsafe_allow_html=True)
            
            # Metric 1: Total Queries
            st.markdown(f"""
            <div style="flex: 1; min-width: 120px; background-color: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center;">
                <h3 style="margin:0; font-size: 2.5rem; font-weight: 700; color: #4b6fff;">{stats["total_nodes"]}</h3>
                <p style="margin:0; font-size: 0.9rem; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">Total Queries</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Metric 2: Completed
            completion_percent = (stats["completed"] / stats["total_nodes"] * 100) if stats["total_nodes"] > 0 else 0
            st.markdown(f"""
            <div style="flex: 1; min-width: 120px; background-color: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center;">
                <h3 style="margin:0; font-size: 2.5rem; font-weight: 700; color: #28a745;">{stats["completed"]}</h3>
                <p style="margin:0; font-size: 0.9rem; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">Completed ({completion_percent:.1f}%)</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Metric 3: Total Learnings
            st.markdown(f"""
            <div style="flex: 1; min-width: 120px; background-color: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center;">
                <h3 style="margin:0; font-size: 2.5rem; font-weight: 700; color: #fd7e14;">{stats["total_learnings"]}</h3>
                <p style="margin:0; font-size: 0.9rem; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">Insights Gathered</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Metric 4: Sources
            st.markdown(f"""
            <div style="flex: 1; min-width: 120px; background-color: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center;">
                <h3 style="margin:0; font-size: 2.5rem; font-weight: 700; color: #6f42c1;">{len(results['visited_urls'])}</h3>
                <p style="margin:0; font-size: 0.9rem; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px;">Sources Referenced</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
                
            # Display progress bar
            st.markdown('<p style="font-weight: 600; margin-top: 20px;">Overall Research Progress</p>', unsafe_allow_html=True)
            display_progress_bar(stats["completed"], stats["total_nodes"])
            
            # Display statistics by depth with improved styling
            if stats["by_depth"]:
                st.markdown('<p style="font-weight: 600; margin-top: 20px;">Queries by Research Depth</p>', unsafe_allow_html=True)
                
                # Create a DataFrame for visualization
                depth_data = []
                for depth, data in sorted(stats["by_depth"].items()):
                    completion_pct = (data['completed']/data['total']*100) if data['total'] > 0 else 0
                    depth_data.append({
                        "Depth": depth,
                        "Queries": data["total"],
                        "Completed": data["completed"],
                        "Learnings": data["learnings"],
                        "Completion %": f"{completion_pct:.1f}%"
                    })
                
                # Show as table with better styling
                df = pd.DataFrame(depth_data)
                st.dataframe(
                    df,
                    use_container_width=True,
                    column_config={
                        "Depth": st.column_config.NumberColumn(
                            "Research Depth",
                            help="How deep in the research tree",
                            format="%d"
                        ),
                        "Completion %": st.column_config.ProgressColumn(
                            "Completion",
                            help="Percentage of queries completed",
                            format="%s",
                            min_value=0,
                            max_value=100,
                        ),
                    },
                    hide_index=True,
                )
        else:
            st.write("Research statistics not available.")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display learnings with prettier formatting
        st.markdown("""
        <div class="card">
            <p class="subheader" style="margin-top:0;">Key Learnings & Insights</p>
            <p class="info-text">The most important findings from your research</p>
        """, unsafe_allow_html=True)
        
        for i, learning in enumerate(results['learnings']):
            st.markdown(f"""
            <div style="background-color: white; border-radius: 8px; padding: 12px; margin-bottom: 10px; border-left: 4px solid {['#4b6fff', '#fd7e14', '#28a745', '#6f42c1', '#dc3545'][i % 5]}; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <p style="margin:0; font-weight: 500;">{i+1}. {learning}</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display visited sources with better table styling
        st.markdown("""
        <div class="card">
            <p class="subheader" style="margin-top:0;">Research Sources</p>
            <p class="info-text">References and sources analyzed during the research process</p>
        """, unsafe_allow_html=True)
        
        sources_df = pd.DataFrame([
            {"Title": data['title'], "URL": data['link']} 
            for data in results['visited_urls'].values()
        ])
        
        if not sources_df.empty:
            # Create a more interactive table
            st.dataframe(
                sources_df,
                use_container_width=True,
                column_config={
                    "URL": st.column_config.LinkColumn("Source URL"),
                },
                hide_index=True,
            )
        else:
            st.write("No sources found.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display research tree with improved styling
        st.markdown("""
        <div class="card">
            <p class="subheader" style="margin-top:0;">Research Tree Visualization</p>
            <p class="info-text">Visual representation of the research process and structure</p>
        """, unsafe_allow_html=True)
        
        if tree_data:
            # Create tabs for different visualization types
            tree_tab1, tree_tab2 = st.tabs(["Interactive Visualization", "Text-Based Tree View"])
            
            with tree_tab1:
                st.write("This interactive visualization shows the complete research tree structure:")
                display_research_tree(tree_data)
            
            with tree_tab2:
                st.write("Text-based representation of the research tree structure:")
                display_text_tree(tree_data)
            
            # Download button for tree data with better styling
            if os.path.exists(tree_path):
                st.markdown(
                    get_binary_file_downloader_html(
                        tree_path, 
                        'Research Tree', 
                        "📥 Download Research Tree (JSON)"
                    ),
                    unsafe_allow_html=True
                )
        else:
            st.write("Research tree visualization not available.")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display final report with better formatting
        st.markdown("""
        <div class="card">
            <p class="subheader" style="margin-top:0;">Final Research Report</p>
            <p class="info-text">Comprehensive report of all research findings with citations</p>
        """, unsafe_allow_html=True)
        
        report_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "results", 
            f"report_{results['sanitized_query']}.md"
        )
        
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            # Create a nice container for the report
            st.markdown('<div style="background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
            st.markdown(report_content)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Word count and download in a footer area
            word_count = len(report_content.split())
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown(f"""
                <div style="background-color: rgba(75, 111, 255, 0.1); border-radius: 4px; padding: 10px; text-align: center;">
                    <p style="margin:0;"><strong>Report Statistics:</strong> {word_count} words, {len(report_content)} characters</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col2:
                st.markdown(
                    get_binary_file_downloader_html(
                        report_path, 
                        'Research Report', 
                        "📥 Download Full Report (Markdown)"
                    ),
                    unsafe_allow_html=True
                )
                
            # Add new export options section
            st.markdown("""
            <div style="margin-top: 20px; background-color: rgba(75, 111, 255, 0.05); border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <p style="font-weight: 600; color: #4b6fff; margin-bottom: 10px;">Export Options</p>
                <p class="info-text">Export your research report to various formats for sharing and presentation</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create export buttons in a row
            export_col1, export_col2, export_col3, export_col4 = st.columns(4)
            
            with export_col1:
                if st.button("📄 Export to PDF", use_container_width=True):
                    with st.spinner("Generating PDF..."):
                        output_path = os.path.join(
                            os.path.dirname(os.path.abspath(__file__)), 
                            "results", 
                            f"{results['sanitized_query']}.pdf"
                        )
                        pdf_path = ExportUtils.export_to_pdf(report_content, output_path)
                        st.success("PDF generated successfully!")
                        st.markdown(
                            ExportUtils.get_file_download_link(
                                pdf_path,
                                label="Download PDF"
                            ),
                            unsafe_allow_html=True
                        )
                
            with export_col2:
                if st.button("📝 Export to DOCX", use_container_width=True):
                    with st.spinner("Generating DOCX..."):
                        output_path = os.path.join(
                            os.path.dirname(os.path.abspath(__file__)), 
                            "results", 
                            f"{results['sanitized_query']}.docx"
                        )
                        docx_path = ExportUtils.export_to_docx(report_content, output_path)
                        st.success("DOCX generated successfully!")
                        st.markdown(
                            ExportUtils.get_file_download_link(
                                docx_path,
                                label="Download DOCX"
                            ),
                            unsafe_allow_html=True
                        )
                
            with export_col3:
                if st.button("🌐 Export to HTML", use_container_width=True):
                    with st.spinner("Generating HTML..."):
                        output_path = os.path.join(
                            os.path.dirname(os.path.abspath(__file__)), 
                            "results", 
                            f"{results['sanitized_query']}.html"
                        )
                        html_path = ExportUtils.export_to_html(report_content, output_path)
                        st.success("HTML generated successfully!")
                        st.markdown(
                            ExportUtils.get_file_download_link(
                                html_path,
                                label="Download HTML"
                            ),
                            unsafe_allow_html=True
                        )
                
            with export_col4:
                if st.button("🎞️ Export to Presentation", use_container_width=True):
                    with st.spinner("Generating presentation..."):
                        output_path = os.path.join(
                            os.path.dirname(os.path.abspath(__file__)), 
                            "results", 
                            f"{results['sanitized_query']}.pptx"
                        )
                        pptx_path = ExportUtils.export_to_presentation(report_content, output_path)
                        st.success("Presentation generated successfully!")
                        st.markdown(
                            ExportUtils.get_file_download_link(
                                pptx_path,
                                label="Download PPTX"
                            ),
                            unsafe_allow_html=True
                        )
        else:
            st.write("Final report not available.")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # New research button with better styling
        st.markdown("""
        <div style="text-align: center; margin: 40px 0 20px 0;">
            <p class="info-text">Want to explore a different topic?</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Start New Research", type="primary", use_container_width=False):
            st.session_state.research_results = None
            st.session_state.follow_up_questions = []
            st.session_state.follow_up_answered = False
            st.rerun()

if __name__ == "__main__":
    main()