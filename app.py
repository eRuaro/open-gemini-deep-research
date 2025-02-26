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
                .style("fill", d => d.data.status === "completed" ? "#4CAF50" : "#FFC107")
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
        }
        
        // Call the visualization with the data
        visualizeTree(${json.dumps(tree_data)});
    </script>
    """, unsafe_allow_html=True)

# Function to download a file
def get_binary_file_downloader_html(file_path, file_label='File'):
    with open(file_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{os.path.basename(file_path)}">{file_label}</a>'
    return href

# Function to run in a separate thread
async def run_deep_research(query, mode, api_key, follow_up_answers=None):
    deep_search = DeepSearch(api_key, mode=mode)
    
    # Determine research breadth and depth
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
    results = await deep_search.deep_research(
        query=combined_query,
        breadth=breadth,
        depth=depth,
        learnings=[],
        visited_urls={}
    )
    
    # Generate the final report
    final_report = deep_search.generate_final_report(
        query=combined_query,
        learnings=results["learnings"],
        visited_urls=results["visited_urls"],
        sanitized_query=results["sanitized_query"]
    )
    
    return {
        "breadth": breadth,
        "depth": depth,
        "explanation": breadth_and_depth["explanation"],
        "learnings": results["learnings"],
        "visited_urls": results["visited_urls"],
        "final_report": final_report,
        "sanitized_query": results["sanitized_query"]
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
    mode = st.sidebar.selectbox(
        "Research Mode",
        ["fast", "balanced", "comprehensive"],
        index=1,  # Default to balanced
        help="Fast: Quick overview, Balanced: Good compromise, Comprehensive: Deep detailed analysis"
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
        - **Comprehensive**: Maximum detail and coverage
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
            
            # Start the research process
            with st.spinner("Researching... This may take several minutes depending on the complexity."):
                try:
                    # Run the research asynchronously
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    start_time = time.time()
                    results = loop.run_until_complete(run_deep_research(query, mode, api_key, follow_up_answers))
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
        
        # Try to load the research tree from file
        tree_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "results", 
            f"research_tree_{results['sanitized_query']}.json"
        )
        
        if os.path.exists(tree_path):
            with open(tree_path, 'r') as f:
                tree_data = json.load(f)
                display_research_tree(tree_data)
                
                # Download button for tree data
                st.markdown(
                    get_binary_file_downloader_html(tree_path, 'Download Research Tree (JSON)'),
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
            
            # Download button for report
            st.markdown(
                get_binary_file_downloader_html(report_path, 'Download Report (Markdown)'),
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