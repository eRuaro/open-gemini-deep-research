from typing import Callable, List, TypeVar, Any, Dict
import asyncio
import datetime
import json
import os
import uuid
import time
import random
import re
import math

from dotenv import load_dotenv

# Import our new GeminiClient
from .gemini_client import GeminiClient


class ResearchProgress:
    def __init__(self, depth: int, breadth: int):
        self.total_depth = depth
        self.total_breadth = breadth
        self.current_depth = depth
        self.current_breadth = 0
        self.queries_by_depth = {}
        self.query_order = []  # Track order of queries
        self.query_parents = {}  # Track parent-child relationships
        self.total_queries = 0  # Total number of queries including sub-queries
        self.completed_queries = 0
        self.query_ids = {}  # Store persistent IDs for queries
        self.root_query = None  # Store the root query

    def start_query(self, query: str, depth: int, parent_query: str = None):
        """Record the start of a new query"""
        if depth not in self.queries_by_depth:
            self.queries_by_depth[depth] = {}

        if query not in self.queries_by_depth[depth]:
            # Generate ID only once per query
            if query not in self.query_ids:
                self.query_ids[query] = str(uuid.uuid4())
                
            self.queries_by_depth[depth][query] = {
                "completed": False,
                "learnings": [],
                "id": self.query_ids[query]  # Use persistent ID
            }
            self.query_order.append(query)
            if parent_query:
                self.query_parents[query] = parent_query
            else:
                self.root_query = query  # Set as root if no parent
            self.total_queries += 1

        self.current_depth = depth
        self.current_breadth = len(self.queries_by_depth[depth])
        self._report_progress(f"Starting query: {query}")

    def add_learning(self, query: str, depth: int, learning: str):
        """Record a learning for a specific query"""
        if depth in self.queries_by_depth and query in self.queries_by_depth[depth]:
            if learning not in self.queries_by_depth[depth][query]["learnings"]:
                self.queries_by_depth[depth][query]["learnings"].append(learning)
                self._report_progress(f"Added learning for query: {query}")

    def complete_query(self, query: str, depth: int):
        """Mark a query as completed"""
        if depth in self.queries_by_depth and query in self.queries_by_depth[depth]:
            if not self.queries_by_depth[depth][query]["completed"]:
                self.queries_by_depth[depth][query]["completed"] = True
                self.completed_queries += 1
                self._report_progress(f"Completed query: {query}")

                # Check if parent query exists and update its status if all children are complete
                parent_query = self.query_parents.get(query)
                if parent_query:
                    self._update_parent_status(parent_query)

    def _update_parent_status(self, parent_query: str):
        """Update parent query status based on children completion"""
        # Find all children of this parent
        children = [q for q, p in self.query_parents.items() if p == parent_query]
        
        # Check if all children are complete
        parent_depth = next((d for d, queries in self.queries_by_depth.items() 
                           if parent_query in queries), None)
        
        if parent_depth is not None:
            all_children_complete = all(
                self.queries_by_depth[d][q]["completed"]
                for q in children
                for d in self.queries_by_depth
                if q in self.queries_by_depth[d]
            )
            
            if all_children_complete:
                # Complete the parent query
                self.complete_query(parent_query, parent_depth)

    def _report_progress(self, action: str):
        """Report current progress with improved visualization"""
        print(f"\n{'-'*80}")
        print(f"\033[1mRESEARCH PROGRESS UPDATE\033[0m")
        print(f"Action: {action}")
        
        # Calculate and display a progress bar
        progress_percent = (self.completed_queries / self.total_queries) * 100 if self.total_queries > 0 else 0
        bar_length = 40
        filled_length = int(bar_length * self.completed_queries // self.total_queries) if self.total_queries > 0 else 0
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        print(f"\nProgress: [{bar}] {progress_percent:.1f}% ({self.completed_queries}/{self.total_queries} queries)")

        # Build tree but only display a simplified version for better readability
        if self.root_query:
            tree = self._build_research_tree()
            print("\nResearch Tree Structure:")
            self._print_tree_pretty(tree)
            
        print(f"{'-'*80}\n")
        
    def _print_tree_pretty(self, node, indent="", is_last=True, is_root=True):
        """Print a more readable tree structure"""
        # Display information about the current node
        if is_root:
            print(f"{indent}📊 Root: \033[1m{node['query'][:50]}{'...' if len(node['query']) > 50 else ''}\033[0m [{node['status']}]")
        else:
            branch = "└── " if is_last else "├── "
            status_icon = "✅" if node['status'] == 'completed' else "🔄"
            print(f"{indent}{branch}{status_icon} \033[1m{node['query'][:50]}{'...' if len(node['query']) > 50 else ''}\033[0m")
            
            # Display number of learnings
            if node['learnings']:
                print(f"{indent}{'    ' if is_last else '│   '}📝 {len(node['learnings'])} learnings")
        
        # Calculate indent for children
        if not is_root:
            indent += "    " if is_last else "│   "
        
        # Recursively print child nodes
        for i, child in enumerate(node['sub_queries']):
            is_last_child = i == len(node['sub_queries']) - 1
            self._print_tree_pretty(child, indent, is_last_child, False)

    def _build_research_tree(self):
        """Build the full research tree structure"""
        def build_node(query):
            """Recursively build the tree node"""
            # Find the depth for this query
            depth = next((d for d, queries in self.queries_by_depth.items() 
                         if query in queries), 0)
            
            data = self.queries_by_depth[depth][query]
            
            # Find all children of this query
            children = [q for q, p in self.query_parents.items() if p == query]
            
            return {
                "query": query,
                "id": self.query_ids[query],
                "status": "completed" if data["completed"] else "in_progress",
                "depth": depth,
                "learnings": data["learnings"],
                "sub_queries": [build_node(child) for child in children],
                "parent_query": self.query_parents.get(query)
            }

        # Start building from the root query
        if self.root_query:
            return build_node(self.root_query)
        return {}

    def get_learnings_by_query(self):
        """Get all learnings organized by query"""
        learnings = {}
        for depth, queries in self.queries_by_depth.items():
            for query, data in queries.items():
                if data["learnings"]:
                    learnings[query] = data["learnings"]
        return learnings


load_dotenv()

class DeepSearch:
    def __init__(self, api_key: str, mode: str = "balanced"):
        """
        Initialize DeepSearch with a mode parameter:
        - "fast": Prioritizes speed (reduced breadth/depth, highest concurrency)
        - "balanced": Default balance of speed and comprehensiveness
        - "comprehensive": Maximum detail and coverage
        """
        self.api_key = api_key
        self.mode = mode
        self.query_history = set()
        
        # Initialize our Gemini client
        self.client = GeminiClient(api_key)
        
        # Ensure results directory exists
        self.results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
        os.makedirs(self.results_dir, exist_ok=True)

    def determine_research_breadth_and_depth(self, query: str):
        user_prompt = f"""
		You are a research planning assistant. Your task is to determine the appropriate breadth and depth for researching a topic defined by a user's query. Evaluate the query's complexity and scope, then recommend values on the following scales:

		Breadth: Scale of 1 (very narrow) to 10 (extensive, multidisciplinary).
		Depth: Scale of 1 (basic overview) to 5 (highly detailed, in-depth analysis).
		Defaults:

		Breadth: 4
		Depth: 2
		Note: More complex or "harder" questions should prompt higher ratings on one or both scales, reflecting the need for more extensive research and deeper analysis.

		Response Format:
		Output your recommendation in JSON format, including an explanation. For example:
		```json
		{{
			"breadth": 4,
			"depth": 2,
			"explanation": "The topic is moderately complex; a broad review is needed (breadth 4) with a basic depth analysis (depth 2)."
		}}
		```

		Here is the user's query:
		<query>{query}</query>
		"""

        schema = {
            "type": "OBJECT",
            "required": ["breadth", "depth", "explanation"],
            "properties": {
                "breadth": {"type": "NUMBER"},
                "depth": {"type": "NUMBER"},
                "explanation": {"type": "STRING"},
            },
        }

        return self.client.generate_json_content(user_prompt, schema)

    def generate_follow_up_questions(self, query: str, max_questions: int = 3):
        user_prompt = f"""
		Given the following query from the user, ask some follow up questions to clarify the research direction.

		Return a maximum of {max_questions} questions, but feel free to return less if the original query is clear: <query>{query}</query>
		"""

        schema = {
            "type": "OBJECT",
            "required": ["follow_up_queries"],
            "properties": {
                "follow_up_queries": {
                    "type": "ARRAY",
                    "items": {
                        "type": "STRING",
                    },
                },
            },
        }

        result = self.client.generate_json_content(user_prompt, schema)
        return result["follow_up_queries"]

    def generate_queries(
            self,
            query: str,
            num_queries: int = 3,
            learnings: list[str] = [],
            previous_queries: set[str] = None
    ):
        now = datetime.datetime.now().strftime("%Y-%m-%d")

        # Format previous queries for the prompt
        previous_queries_text = ""
        if previous_queries:
            previous_queries_text = "\n\nPreviously asked queries (avoid generating similar ones):\n" + \
                "\n".join([f"- {q}" for q in previous_queries])

        user_prompt = f"""
        Given the following prompt from the user, generate a list of SERP queries to research the topic. Return a maximum
        of {num_queries} queries, but feel free to return less if the original prompt is clear.

        IMPORTANT: Each query must be unique and significantly different from both each other AND the previously asked queries.
        Avoid semantic duplicates or queries that would likely return similar information.

        Original prompt: <prompt>${query}</prompt>
        {previous_queries_text}
        """

        learnings_prompt = "" if not learnings else "Here are some learnings from previous research, use them to generate more specific queries: " + \
            "\n".join(learnings)

        schema = {
            "type": "OBJECT",
            "required": ["queries"],
            "properties": {
                "queries": {
                    "type": "ARRAY",
                    "items": {
                        "type": "STRING",
                    },
                },
            },
        }

        result = self.client.generate_json_content(user_prompt + learnings_prompt, schema)
        return result["queries"]

    def search(self, query: str):
        return self.client.search(query)

    async def process_result(
        self,
        query: str,
        result: str,
        num_learnings: int = 3,
        num_follow_up_questions: int = 3,
    ):
        print(f"Processing result for query: {query}")

        user_prompt = f"""
		Given the following result from a SERP search for the query <query>{query}</query>, generate a list of learnings from the result. Return a maximum of {num_learnings} learnings, but feel free to return less if the result is clear. Make sure each learning is unique and not similar to each other. The learnings should be concise and to the point, as detailed and information dense as possible. Make sure to include any entities like people, places, companies, products, things, etc in the learnings, as well as any exact metrics, numbers, or dates. The learnings will be used to research the topic further.
		"""

        schema = {
            "type": "OBJECT",
            "required": ["learnings", "follow_up_questions"],
            "properties": {
                "learnings": {
                    "type": "ARRAY",
                    "items": {
                        "type": "STRING"
                    }
                },
                "follow_up_questions": {
                    "type": "ARRAY",
                    "items": {
                        "type": "STRING"
                    }
                }
            },
        }

        answer_json = self.client.generate_json_content(user_prompt + "\n" + result, schema)

        learnings = answer_json["learnings"]
        follow_up_questions = answer_json["follow_up_questions"]

        print(f"Results from {query}:")
        print(f"Learnings: {learnings}\n")
        print(f"Follow up questions: {follow_up_questions}\n")

        return answer_json

    def _are_queries_similar(self, query1: str, query2: str) -> bool:
        """Helper method to check if two queries are semantically similar using Gemini"""
        user_prompt = f"""
        Compare these two search queries and determine if they are semantically similar 
        (i.e., would likely return similar search results or are asking about the same topic):

        Query 1: {query1}
        Query 2: {query2}

        Consider:
        1. Key concepts and entities
        2. Intent of the queries
        3. Scope and specificity
        4. Core topic overlap

        Only respond with true if the queries are notably similar, false otherwise.
        """

        schema = {
            "type": "OBJECT",
            "required": ["are_similar"],
            "properties": {
                "are_similar": {
                    "type": "BOOLEAN",
                    "description": "True if queries are semantically similar, false otherwise"
                }
            }
        }

        try:
            result = self.client.generate_json_content(user_prompt, schema)
            return result["are_similar"]
        except Exception as e:
            print(f"Error comparing queries: {str(e)}")
            # In case of error, assume queries are different to avoid missing potentially unique results
            return False

    def _sanitize_filename(self, query: str) -> str:
        """Convert a query to a valid filename by removing invalid characters and truncating if needed"""
        # Replace newlines with spaces first
        sanitized = query.replace('\n', ' ').replace('\r', ' ')
        
        # Replace invalid filename characters with underscores
        sanitized = re.sub(r'[\\/*?:"<>|]', "_", sanitized)
        
        # Replace spaces with underscores for better filenames
        sanitized = sanitized.replace(" ", "_")
        
        # Remove consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        
        # Truncate if too long (max 100 chars for filename)
        if len(sanitized) > 100:
            sanitized = sanitized[:97] + "..."
            
        # Add timestamp to ensure uniqueness
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{sanitized}_{timestamp}"

    async def deep_research(self, query: str, breadth: int, depth: int, learnings: list[str] = [], visited_urls: dict[int, dict] = {}, parent_query: str = None):
        print(f"\n{'='*80}")
        print(f"\033[1m🔍 STARTING DEEP RESEARCH\033[0m")
        print(f"Mode: {self.mode.capitalize()}")
        print(f"Breadth: {breadth}, Depth: {depth}")
        print(f"{'='*80}\n")
        
        progress = ResearchProgress(depth, breadth)
        
        # Start the root query
        progress.start_query(query, depth, parent_query)

        # Adjust number of queries based on mode
        max_queries = {
            "fast": 3,
            "balanced": 7,
            "comprehensive": 5 # kept lower than balanced due to recursive multiplication
        }[self.mode]

        print(f"Generating research queries...", end="", flush=True)
        queries = self.generate_queries(
            query,
            min(breadth, max_queries),
            learnings,
            previous_queries=self.query_history
        )
        print(f" Done! Generated {len(queries)} queries.")

        self.query_history.update(queries)
        unique_queries = list(queries)[:breadth]

        print(f"\n📋 Primary research queries:")
        for i, q in enumerate(unique_queries):
            print(f"  {i+1}. {q}")
        print()

        async def process_query(query_str: str, current_depth: int, parent: str = None):
            try:
                # Start this query as a sub-query of the parent
                progress.start_query(query_str, current_depth, parent)

                print(f"🔎 Searching for: \033[1m{query_str[:50]}{'...' if len(query_str) > 50 else ''}\033[0m")
                result = self.search(query_str)
                print(f"✓ Found {len(result[1])} sources")
                
                processed_result = await self.process_result(
                    query=query_str,
                    result=result[0],
                    num_learnings=min(3, math.ceil(breadth / 2)),
                    num_follow_up_questions=min(2, math.ceil(breadth / 2))
                )

                # Record learnings
                for learning in processed_result["learnings"]:
                    progress.add_learning(query_str, current_depth, learning)

                new_urls = result[1]
                max_idx = max(visited_urls.keys()) if visited_urls else -1
                all_urls = {
                    **visited_urls,
                    **{(i + max_idx + 1): url_data for i, url_data in new_urls.items()}
                }

                # Only go deeper if in comprehensive mode and depth > 1
                if self.mode == "comprehensive" and current_depth > 1:
                    # Reduced breadth for deeper levels
                    new_breadth = min(2, math.ceil(breadth / 2))
                    new_depth = current_depth - 1

                    # Select most important follow-up question instead of using all
                    if processed_result['follow_up_questions']:
                        # Take only the most relevant question
                        next_query = processed_result['follow_up_questions'][0]
                        
                        print(f"\n📥 Going deeper with follow-up question: \033[1m{next_query[:50]}{'...' if len(next_query) > 50 else ''}\033[0m\n")
                        
                        # Process the sub-query
                        sub_results = await process_query(
                            next_query,
                            new_depth,
                            query_str  # Pass current query as parent
                        )

                progress.complete_query(query_str, current_depth)
                return {
                    "learnings": processed_result["learnings"],
                    "visited_urls": all_urls
                }

            except Exception as e:
                print(f"\n❌ Error processing query \033[1m{query_str[:50]}{'...' if len(query_str) > 50 else ''}\033[0m: {str(e)}")
                progress.complete_query(query_str, current_depth)
                return {
                    "learnings": [],
                    "visited_urls": {}
                }

        print(f"\n🚀 Starting parallel research on {len(unique_queries)} queries...\n")
        
        # Process queries concurrently
        tasks = [process_query(q, depth, query) for q in unique_queries]
        results = await asyncio.gather(*tasks)

        # Combine results
        all_learnings = list(set(
            learning
            for result in results
            for learning in result["learnings"]
        ))

        all_urls = {}
        current_idx = 0
        seen_urls = set()
        for result in results:
            for url_data in result["visited_urls"].values():
                if url_data['link'] not in seen_urls:
                    all_urls[current_idx] = url_data
                    seen_urls.add(url_data['link'])
                    current_idx += 1

        # Complete the root query after all sub-queries are done
        progress.complete_query(query, depth)

        # Create sanitized filename from query
        sanitized_query = self._sanitize_filename(query)
        
        # Save the tree structure to a json file in results folder
        tree_filename = os.path.join(self.results_dir, f"research_tree_{sanitized_query}.json")
        with open(tree_filename, "w") as f:
            json.dump(progress._build_research_tree(), f)
        
        # Display a summary of research results
        print(f"\n{'='*80}")
        print(f"\033[1m📊 RESEARCH SUMMARY\033[0m")
        print(f"Total queries processed: {progress.total_queries}")
        print(f"Total learnings gathered: {len(all_learnings)}")
        print(f"Total unique sources found: {len(all_urls)}")
        print(f"\n📂 Research tree saved to: {tree_filename}")
        print(f"{'='*80}\n")

        return {
            "learnings": all_learnings,
            "visited_urls": all_urls,
            "sanitized_query": sanitized_query,  # Return this for use in generate_final_report
            "research_tree": progress._build_research_tree()  # Return the full tree for display
        }

    def generate_final_report(self, query: str, learnings: list[str], visited_urls: dict[int, dict], sanitized_query: str = None) -> str:
        print(f"\n{'='*80}")
        print(f"\033[1m📝 GENERATING FINAL RESEARCH REPORT\033[0m")
        print(f"{'='*80}\n")
        
        # If no sanitized_query provided, create one
        if sanitized_query is None:
            sanitized_query = self._sanitize_filename(query)
            
        # Format sources and learnings for the prompt
        sources_text = "\n".join([
            f"- {data['title']}: {data['link']}"
            for data in visited_urls.values()
        ])
        learnings_text = "\n".join([f"- {learning}" for learning in learnings])

        print(f"📊 Synthesizing {len(learnings)} key learnings from {len(visited_urls)} sources...")
        
        user_prompt = f"""
        You are a creative research analyst tasked with synthesizing findings into an engaging and informative report.
        Create a comprehensive research report (minimum 3000 words) based on the following query and findings.
        
        Original Query: {query}
        
        Key Findings:
        {learnings_text}
        
        Sources Used:
        {sources_text}
        
        Guidelines:
        1. Design a creative and engaging report structure that best fits the content and topic
        2. Feel free to use any combination of:
           - Storytelling elements
           - Case studies
           - Scenarios
           - Visual descriptions
           - Analogies and metaphors
           - Creative section headings
           - Thought experiments
           - Future projections
           - Historical parallels
        3. Make the report engaging while maintaining professionalism
        4. Include all relevant data points but present them in an interesting way
        5. Structure the information in whatever way makes the most logical sense for this specific topic
        6. Feel free to break conventional report formats if a different approach would be more effective
        7. Consider using creative elements like:
           - "What if" scenarios
           - Day-in-the-life examples
           - Before/After comparisons
           - Expert perspectives
           - Trend timelines
           - Problem-solution frameworks
           - Impact matrices
        
        Requirements:
        - Minimum 3000 words
        - Must include all key findings and data points
        - Must maintain factual accuracy
        - Must be well-organized and easy to follow
        - Must include clear conclusions and insights
        - Must cite sources appropriately
        
        Be bold and creative in your approach while ensuring the report effectively communicates all the important information!
        """

        generation_config = {
            "temperature": 0.9,  # Increased for more creativity
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }

        print("🧠 Generating report content... (this might take a few minutes)")
        print("⏳ AI is working on synthesizing information and drafting the report...")

        response = self.client.generate_content(user_prompt, generation_config)
        print("✓ Initial report content generated!")
        
        print("📋 Formatting report with citations...")
        # Format the response with inline citations
        formatted_text, sources = self.client.format_text_with_sources(
            response.to_dict(),
            response.text
        )
        
        # Add sources section
        sources_section = "\n# Sources\n" + "\n".join([
            f"- [{data['title']}]({data['link']})"
            for data in visited_urls.values()
        ])
        
        report_content = formatted_text + sources_section
        
        # Save the report to a file in the results folder
        report_filename = os.path.join(self.results_dir, f"report_{sanitized_query}.md")
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(report_content)
            
        print(f"\n✅ Final report successfully generated!")
        print(f"📂 Report saved to: {report_filename}")
        print(f"\n{'='*80}\n")

        # Count approximate words for the user
        word_count = len(report_content.split())
        print(f"📊 Report statistics:")
        print(f"  - Word count: approximately {word_count} words")
        print(f"  - Sources cited: {len(visited_urls)} unique sources")
        print(f"  - Insights incorporated: {len(learnings)} key learnings\n")

        return report_content