import argparse
import asyncio
import os
import time
import json
from pathlib import Path
from src.deep_research import DeepSearch
from src.export_utils import ExportUtils

def display_title():
    """Display a fancy title for the application"""
    title = r"""
    ╔═══════════════════════════════════════════════════════╗
    ║           OPEN GEMINI DEEP RESEARCH SYSTEM            ║
    ╚═══════════════════════════════════════════════════════╝
    """
    print(title)

def display_summary(results, elapsed_time):
    """Display a summary of research results"""
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    print(f"\n{'='*80}")
    print(f"\033[1m📊 RESEARCH COMPLETED\033[0m")
    print(f"{'='*80}")
    print(f"Total research time: {minutes} minutes and {seconds} seconds")
    
    # Display research tree summary if available
    if "research_tree" in results:
        tree = results["research_tree"]
        print("\n🌳 Research Tree Overview:")
        count_by_depth = {}
        
        # Function to count nodes by depth
        def count_nodes_by_depth(node, current_depth=0):
            if current_depth not in count_by_depth:
                count_by_depth[current_depth] = {'total': 0, 'completed': 0}
            
            count_by_depth[current_depth]['total'] += 1
            if node["status"] == "completed":
                count_by_depth[current_depth]['completed'] += 1
                
            for child in node["sub_queries"]:
                count_nodes_by_depth(child, current_depth + 1)
        
        # Count nodes
        if tree:
            count_nodes_by_depth(tree)
            
            # Display summary
            for depth, counts in sorted(count_by_depth.items()):
                print(f"  Depth {depth}: {counts['completed']}/{counts['total']} queries completed")

    sanitized_query = results.get('sanitized_query', 'research')
    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    os.makedirs(results_dir, exist_ok=True)

    # Save the research outputs
    report_path = os.path.join(results_dir, f"report_{sanitized_query}.md")
    tree_path = os.path.join(results_dir, f"research_tree_{sanitized_query}.json")
    
    print(f"\n📚 Final Report generated and saved to:")
    print(f"  - {report_path}")
    
    print(f"\n🔍 Research Tree saved to:")
    print(f"  - {tree_path}")
    
    print("\n📤 Export Options:")
    print("  1. PDF     (pdf)")
    print("  2. Word    (docx)")
    print("  3. HTML    (html)")
    print("  4. PowerPoint (pptx)")
    print("  5. Skip export")
    
    while True:
        try:
            choice = input("\nEnter export format (pdf/docx/html/pptx) or press Enter to skip: ").lower().strip()
            if not choice:
                break
                
            if choice not in ['pdf', 'docx', 'html', 'pptx']:
                print("Invalid choice. Please try again.")
                continue
                
            # Read the markdown content from the results directory
            with open(report_path, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            output_path = os.path.join(results_dir, f"{sanitized_query}.{choice}")
            print(f"\n⚙️ Generating {choice.upper()} export...")
            
            if choice == 'pdf':
                ExportUtils.export_to_pdf(report_content, output_path)
            elif choice == 'docx':
                ExportUtils.export_to_docx(report_content, output_path)
            elif choice == 'html':
                ExportUtils.export_to_html(report_content, output_path)
            elif choice == 'pptx':
                ExportUtils.export_to_presentation(report_content, output_path)
            
            print(f"✅ Export complete! File saved to: {output_path}")
            
            export_another = input("\nWould you like to export in another format? (y/N): ").lower().strip()
            if export_another != 'y':
                break
                
        except Exception as e:
            print(f"❌ Export failed: {str(e)}")
            print("Please try again or skip export.")
    
    print(f"{'='*80}")

if __name__ == "__main__":
    display_title()
    
    parser = argparse.ArgumentParser(description='Run deep search queries')
    parser.add_argument('query', type=str, help='The search query')
    parser.add_argument('--mode', type=str, choices=['fast', 'balanced', 'comprehensive'],
                        default='balanced', help='Research mode (default: balanced)')
    parser.add_argument('--num-queries', type=int, default=3,
                        help='Number of queries to generate (default: 3)')
    parser.add_argument('--learnings', nargs='*', default=[],
                        help='List of previous learnings')

    args = parser.parse_args()

    # Start the timer
    start_time = time.time()

    # Get API key from environment variable
    api_key = os.getenv('GEMINI_KEY')
    if not api_key:
        raise ValueError("Please set GEMINI_KEY environment variable")

    print(f"\n🔧 Setting up research parameters for: \033[1m{args.query}\033[0m")
    print(f"Mode: {args.mode}")
    
    deep_search = DeepSearch(api_key, mode=args.mode)

    print("📐 Analyzing query complexity...", end="", flush=True)
    breadth_and_depth = deep_search.determine_research_breadth_and_depth(
        args.query)
    print(" Done!")

    breadth = breadth_and_depth["breadth"]
    depth = breadth_and_depth["depth"]
    explanation = breadth_and_depth["explanation"]

    print(f"\n📊 Analysis Results:")
    print(f"  Breadth: {breadth}/10 ({explanation.split('.')[0]})")
    print(f"  Depth: {depth}/5")
    print(f"  Explanation: {explanation}")

    print("\n❓ To better understand your research needs, please answer these follow-up questions:")
    follow_up_questions = deep_search.generate_follow_up_questions(args.query)

    # get answers to the follow up questions
    answers = []
    for question in follow_up_questions:
        answer = input(f"  \033[1m{question}\033[0m: ")
        answers.append({
            "question": question,
            "answer": answer
        })

    questions_and_answers = "\n".join(
        [f"{answer['question']}: {answer['answer']}"] for answer in answers)

    combined_query = f"Initial query: {args.query}\n\n Follow up questions and answers: {questions_and_answers}"

    print(f"\n📋 Combined Query (used for research):")
    print(f"  {combined_query.replace(chr(10), ' ')[:100]}...")

    print(f"\n{'='*80}")
    print(f"\033[1m🚀 STARTING RESEARCH\033[0m")
    print(f"{'='*80}")

    # Run the deep research
    results = asyncio.run(deep_search.deep_research(
        query=combined_query,
        breadth=breadth,
        depth=depth,
        learnings=[],
        visited_urls={}
    ))

    # Generate and print the final report
    final_report = deep_search.generate_final_report(
        query=combined_query,
        learnings=results["learnings"],
        visited_urls=results["visited_urls"],
        sanitized_query=results.get("sanitized_query")
    )

    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    # Display summary of the research
    display_summary(results, elapsed_time)
    
    print(f"\n📝 Open {os.path.join('results', f'report_{results.get("sanitized_query", "research")}.md')} to view your complete research results")