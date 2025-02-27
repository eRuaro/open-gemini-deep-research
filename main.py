import argparse
import asyncio
import os
import time
import json

from src.deep_research import DeepSearch


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
    
    print(f"\n📚 Final Report generated and saved to:")
    print(f"  - final_report.md (main directory)")
    print(f"  - results/report_{results.get('sanitized_query', 'research')}.md")
    
    print(f"\n🔍 Research Tree saved to:")
    print(f"  - results/research_tree_{results.get('sanitized_query', 'research')}.json")
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
        [f"{answer['question']}: {answer['answer']}" for answer in answers])

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

    # Save the report to a file
    with open("final_report.md", "w", encoding="utf-8") as f:
        f.write(final_report)
        f.write(
            f"\n\nTotal research time: {int(elapsed_time // 60)} minutes and {int(elapsed_time % 60)} seconds")
    
    print("\n📝 Open final_report.md to view your complete research results")