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
    }
    .subheader {
        font-size: 1.5rem;
        color: #6c757d;
    }
    .card {
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
        background-color: #f8f9fa;
        border-left: 5px solid #4b6fff;
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
    }
    .progress-bar {
        height: 10px;
        border-radius: 5px;
        background-color: #4b6fff;
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
    node_class = f"research-tree-node research-tree-node-{tree_data['status']}"
    
    if level == 0:
        st.markdown(f"""
        <div class="{node_class}">
            <h4>📊 Root Query: <span class="{status_class}">{tree_data["query"][:50]}{"..." if len(tree_data["query"]) > 50 else ""}</span></h4>
            <p>Status: <span class="{status_class}">{tree_data["status"].upper()}</span> | Depth: {tree_data["depth"]} | Learnings: {len(tree_data["learnings"])}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        prefix = "&nbsp;" * 4 * level
        emoji = "✅" if tree_data["status"] == "completed" else "🔄"
        st.markdown(f"""
        <div class="{node_class}" style="margin-left: {level * 20}px;">
            <p>{prefix} {emoji} <span class="{status_class}">{tree_data["query"][:50]}{"..." if len(tree_data["query"]) > 50 else ""}</span></p>
            <p>{prefix} Status: <span class="{status_class}">{tree_data["status"].upper()}</span> | Depth: {tree_data["depth"]} | Learnings: {len(tree_data["learnings"])}</p>
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
    <p>Progress: {completed}/{total} queries completed ({percent:.1f}%)</p>
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
        status_placeholder.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h3>🔍 Initializing Research...</h3>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: 5%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    deep_search = DeepSearch(api_key, mode=mode)
    
    # Determine research breadth and depth
    if status_placeholder:
        status_placeholder.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h3>📊 Analyzing Query Complexity...</h3>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: 15%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    breadth_and_depth = deep_search.determine_research_breadth_and_depth(query)
    breadth = breadth_and_depth["breadth"]
    depth = breadth_and_depth["depth"]
    
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
        status_placeholder.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h3>🚀 Running Deep Research...</h3>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: 30%"></div>
            </div>
            <p>Researching multiple sources and extracting insights. This may take several minutes...</p>
        </div>
        """, unsafe_allow_html=True)
    
    results = await deep_search.deep_research(
        query=combined_query,
        breadth=breadth,
        depth=depth,
        learnings=[],
        visited_urls={}
    )
    
    # Generate the final report
    if status_placeholder:
        status_placeholder.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h3>📝 Generating Final Research Report...</h3>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: 75%"></div>
            </div>
            <p>Synthesizing findings into a comprehensive report...</p>
        </div>
        """, unsafe_allow_html=True)
    
    final_report = deep_search.generate_final_report(
        query=combined_query,
        learnings=results["learnings"],
        visited_urls=results["visited_urls"],
        sanitized_query=results["sanitized_query"]
    )
    
    if status_placeholder:
        status_placeholder.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h3>✅ Research Completed!</h3>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: 100%"></div>
            </div>
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
    # Sidebar
    st.sidebar.markdown('<p class="main-header">🔍 Settings</p>', unsafe_allow_html=True)
    
    # API Key input
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password", value=os.getenv('GEMINI_KEY', ''))
    if not api_key:
        st.sidebar.warning("Please enter your Gemini API Key")
    
    # Research mode selection
    mode_descriptions = {
        "fast": "Quick overview with basic insights (1-2 min)",
        "balanced": "Good balance between speed and depth (3-6 min)",
        "comprehensive": "In-depth research with deeper insights (5-15 min)"
    }
    
    mode = st.sidebar.selectbox(
        "Research Mode",
        ["fast", "balanced", "comprehensive"],
        index=1,  # Default to balanced
        format_func=lambda x: f"{x.capitalize()}: {mode_descriptions[x]}"
    )
    
    # About section in sidebar
    with st.sidebar.expander("About Open Gemini Deep Research"):
        st.write("""
        This tool performs deep research using Google's Gemini AI model. 
        It generates queries, processes search results, extracts learnings, 
        and creates a comprehensive research report.
        
        **Modes:**
        - **Fast**: Quick overview with minimal depth
        - **Balanced**: Good compromise between speed and detail
        - **Comprehensive**: Maximum detail and coverage with recursive exploration
        """)
    
    # Main content
    st.markdown('<p class="main-header">🔍 Open Gemini Deep Research</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">AI-powered deep research assistant</p>', unsafe_allow_html=True)
    
    # Query input
    query = st.text_area("Enter your research topic or question:", height=100)
    
    # Initialize session state for follow-up questions
    if 'follow_up_questions' not in st.session_state:
        st.session_state.follow_up_questions = []
        
    if 'research_running' not in st.session_state:
        st.session_state.research_running = False
        
    if 'research_results' not in st.session_state:
        st.session_state.research_results = None
        
    if 'follow_up_answered' not in st.session_state:
        st.session_state.follow_up_answered = False
    
    # Start research button
    col1, col2 = st.columns([1, 5])
    with col1:
        start_button = st.button("Start Research", disabled=not api_key or not query or st.session_state.research_running)
    
    with col2:
        if st.session_state.research_running:
            st.info("Research in progress... This may take several minutes depending on the research mode.")
    
    # Generate follow-up questions when Start button is clicked
    if start_button and api_key and query:
        st.session_state.research_running = True
        st.session_state.follow_up_answered = False
        
        with st.spinner("Generating follow-up questions..."):
            try:
                deep_search = DeepSearch(api_key, mode=mode)
                st.session_state.follow_up_questions = deep_search.generate_follow_up_questions(query)
            except Exception as e:
                st.error(f"Error generating follow-up questions: {str(e)}")
                st.session_state.research_running = False
    
    # Display follow-up questions if available
    if st.session_state.follow_up_questions and not st.session_state.follow_up_answered:
        st.markdown('<div class="card"><p class="subheader">Follow-up Questions</p>', unsafe_allow_html=True)
        st.write("To better understand your research needs, please answer these follow-up questions:")
        
        follow_up_answers = {}
        for question in st.session_state.follow_up_questions:
            follow_up_answers[question] = st.text_input(question)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 5])
        with col1:
            continue_button = st.button("Continue Research")
        
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
        
        # Display research parameters
        st.markdown('<div class="card"><p class="subheader">Research Parameters</p>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Breadth", f"{results['breadth']}/10")
        with col2:
            st.metric("Depth", f"{results['depth']}/5")
        with col3:
            minutes = int(results['elapsed_time'] // 60)
            seconds = int(results['elapsed_time'] % 60)
            st.metric("Research Time", f"{minutes}m {seconds}s")
        
        st.info(results['explanation'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display research statistics
        st.markdown('<div class="card"><p class="subheader">Research Statistics</p>', unsafe_allow_html=True)
        
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
            
            # Display tree statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Queries", stats["total_nodes"])
            with col2:
                st.metric("Completed", stats["completed"])
            with col3:
                st.metric("Total Learnings", stats["total_learnings"])
            with col4:
                st.metric("Sources Found", len(results['visited_urls']))
                
            # Display progress bar
            display_progress_bar(stats["completed"], stats["total_nodes"])
            
            # Display statistics by depth
            if stats["by_depth"]:
                st.subheader("Queries by Research Depth")
                depth_data = []
                for depth, data in sorted(stats["by_depth"].items()):
                    depth_data.append({
                        "Depth": depth,
                        "Queries": data["total"],
                        "Completed": data["completed"],
                        "Learnings": data["learnings"],
                        "Completion %": f"{(data['completed']/data['total']*100) if data['total'] > 0 else 0:.1f}%"
                    })
                st.dataframe(pd.DataFrame(depth_data), use_container_width=True)
        else:
            st.write("Research statistics not available.")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display learnings
        st.markdown('<div class="card"><p class="subheader">Key Learnings</p>', unsafe_allow_html=True)
        for i, learning in enumerate(results['learnings']):
            st.write(f"**{i+1}. {learning}**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display visited sources
        st.markdown('<div class="card"><p class="subheader">Sources</p>', unsafe_allow_html=True)
        sources_df = pd.DataFrame([
            {"Title": data['title'], "URL": data['link']} 
            for data in results['visited_urls'].values()
        ])
        
        if not sources_df.empty:
            st.dataframe(sources_df, use_container_width=True)
        else:
            st.write("No sources found.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display research tree
        st.markdown('<div class="card"><p class="subheader">Research Tree</p>', unsafe_allow_html=True)
        
        if tree_data:
            # Show both visualizations
            st.subheader("Interactive Visualization")
            display_research_tree(tree_data)
            
            st.subheader("Text-Based Tree View")
            display_text_tree(tree_data)
            
            # Download button for tree data
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
        
        # Display final report
        st.markdown('<div class="card"><p class="subheader">Final Report</p>', unsafe_allow_html=True)
        
        report_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "results", 
            f"report_{results['sanitized_query']}.md"
        )
        
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            st.markdown(report_content)
            
            # Word count
            word_count = len(report_content.split())
            st.info(f"Report contains approximately {word_count} words")
            
            # Download button for report
            st.markdown(
                get_binary_file_downloader_html(
                    report_path, 
                    'Research Report', 
                    "📥 Download Report (Markdown)"
                ),
                unsafe_allow_html=True
            )
        else:
            st.write("Final report not available.")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # New research button
        if st.button("Start New Research"):
            st.session_state.research_results = None
            st.session_state.follow_up_questions = []
            st.session_state.follow_up_answered = False
            st.rerun()

if __name__ == "__main__":
    main()