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

# Integrated advanced research techniques including MCTS, adaptive deep research, information value estimation, multi-armed bandit, and knowledge graph.
import math
import random
import asyncio

# Constants for adaptive research parameters
HIGH_THRESHOLD = 0.7
LOW_THRESHOLD = 0.3


class MCTSResearchNode:
    def __init__(self, query, parent=None):
        self.query = query
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0.0
        self.unexplored_actions = []  # Potential follow-up questions

    def select_best_child(self, exploration_weight=1.0):
        # UCB1 formula for balancing exploration/exploitation
        return max(self.children, 
                   key=lambda c: (c.value / c.visits if c.visits > 0 else float('inf')) + exploration_weight * math.sqrt(2 * math.log(self.visits) / c.visits) if c.visits > 0 else float('inf'))


class QueryBandit:
    def __init__(self):
        self.queries = {}  # Query -> [rewards]

    def _calculate_expected_reward(self, query):
        rewards = self.queries.get(query, [1.0])
        return sum(rewards) / len(rewards) if rewards else 1.0

    def select_query(self, available_queries):
        # Thompson sampling implementation
        if random.random() < 0.1:  # Exploration factor
            return random.choice(available_queries)
        
        return max(available_queries, key=lambda q: self._calculate_expected_reward(q))

    def update_reward(self, query, reward):
        if query in self.queries:
            self.queries[query].append(reward)
        else:
            self.queries[query] = [reward]


class ResearchKnowledgeGraph:
    def __init__(self):
        self.entities = set()
        self.relationships = []

    def add_learning(self, learning):
        # Extract entities and relationships from learnings
        new_entities = self._extract_entities(learning)
        self.entities.update(new_entities)
        # Connect related entities
        self._create_relationships(new_entities)

    def _extract_entities(self, learning):
        # Dummy implementation for entity extraction
        return set(learning.split())

    def _create_relationships(self, entities):
        # Dummy implementation: create relationships between all entities
        for e in entities:
            for other in entities:
                if e != other:
                    self.relationships.append((e, other))

    def _connection_count(self, entity):
        return sum(1 for rel in self.relationships if entity in rel)

    def identify_knowledge_gaps(self, threshold=2):
        # Find entities with few connections - research opportunities
        return [e for e in self.entities if self._connection_count(e) < threshold]


async def adaptive_deep_research(query, initial_breadth=4, initial_depth=2, process_query_func=None, calculate_information_density_func=None):
    """
    Adaptive deep research method that adjusts search parameters based on information density.
    :param query: The research query
    :param initial_breadth: Starting breadth
    :param initial_depth: Starting depth
    :param process_query_func: async function to process the query
    :param calculate_information_density_func: function to calculate information density given results
    """
    current_breadth = initial_breadth
    current_depth = initial_depth
    
    if process_query_func is None or calculate_information_density_func is None:
        raise ValueError('process_query_func and calculate_information_density_func must be provided')
    
    results = await process_query_func(query)
    information_density = calculate_information_density_func(results)
    
    # Dynamically adjust parameters
    if information_density > HIGH_THRESHOLD:
        current_depth += 1  # Go deeper on promising branches
        current_breadth = max(2, current_breadth - 1)  # Focus resources
    elif information_density < LOW_THRESHOLD:
        current_breadth += 2  # Explore more broadly when not finding good info
    
    return {
        'results': results,
        'adjusted_breadth': current_breadth,
        'adjusted_depth': current_depth
    }


def estimate_information_value(query, learnings, calculate_novelty_func, calculate_relevance_func, calculate_specificity_func):
    """
    Estimate the information value of a research path based on novelty, relevance, and specificity.
    :param query: The research query
    :param learnings: The collected learnings
    :param calculate_novelty_func: function to calculate novelty
    :param calculate_relevance_func: function to calculate relevance
    :param calculate_specificity_func: function to calculate specificity
    """
    novelty = calculate_novelty_func(learnings)
    relevance = calculate_relevance_func(query, learnings)
    specificity = calculate_specificity_func(learnings)
    
    # Combined score with weighted factors
    return 0.4 * novelty + 0.4 * relevance + 0.2 * specificity


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
        
        # Mode-specific parameters for better scaling
        self.mode_config = {
            "fast": {
                "max_queries": 3,                # Fewer queries for speed
                "max_concurrency": 5,            # Higher concurrency for speed
                "depth_multiplier": 0.7,         # Reduce depth for speed
                "request_timeout": 30,           # Shorter timeout for queries
                "follow_up_multiplier": 0.5,     # Fewer follow-ups
                "max_recursive_depth": 1,        # Minimal recursion
                "learning_density": 2,           # Fewer learnings per query
                "report_detail_level": "brief",  # Brief report
                "section_batch_size": 5          # Process more sections at once
            },
            "balanced": {
                "max_queries": 7,                # Balanced number of queries
                "max_concurrency": 3,            # Moderate concurrency
                "depth_multiplier": 1.0,         # Standard depth
                "request_timeout": 45,           # Standard timeout
                "follow_up_multiplier": 1.0,     # Standard follow-ups
                "max_recursive_depth": 2,        # Standard recursion
                "learning_density": 3,           # Standard learnings per query
                "report_detail_level": "standard", # Standard report detail
                "section_batch_size": 3          # Standard batch size
            },
            "comprehensive": {
                "max_queries": 5,                # Fewer but more targeted queries
                "max_concurrency": 2,            # Lower concurrency for thoroughness
                "depth_multiplier": 1.5,         # Increased depth
                "request_timeout": 60,           # Longer timeout for thorough responses
                "follow_up_multiplier": 2.0,     # More follow-ups
                "max_recursive_depth": 3,        # Maximum recursive exploration
                "learning_density": 5,           # More learnings per query
                "report_detail_level": "detailed", # More detailed report
                "section_batch_size": 2          # Smaller batch size for higher quality
            }
        }
        
        # Initialize our Gemini client
        self.client = GeminiClient(api_key)
        
        # Ensure results directory exists
        self.results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
        os.makedirs(self.results_dir, exist_ok=True)

        # Create knowledge graph for tracking research insights
        self.knowledge_graph = ResearchKnowledgeGraph()

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
        
        # Apply mode-specific scaling factors
        config = self.mode_config[self.mode]
        effective_depth = math.ceil(depth * config['depth_multiplier'])
        max_concurrency = config['max_concurrency']
        max_queries = config['max_queries']
        max_recursive_depth = config['max_recursive_depth']
        
        progress = ResearchProgress(effective_depth, breadth)
        
        # Start the root query
        progress.start_query(query, effective_depth, parent_query)

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

        # Create a query bandit to optimize query selection
        query_bandit = QueryBandit()

        async def process_query(query_str: str, current_depth: int, parent: str = None):
            try:
                # Start this query as a sub-query of the parent
                progress.start_query(query_str, current_depth, parent)

                print(f"🔎 Searching for: \033[1m{query_str[:50]}{'...' if len(query_str) > 50 else ''}\033[0m")
                result = self.search(query_str)
                print(f"✓ Found {len(result[1])} sources")
                
                # Use mode-specific learning density
                learning_density = config["learning_density"]
                
                processed_result = await self.process_result(
                    query=query_str,
                    result=result[0],
                    num_learnings=learning_density,
                    num_follow_up_questions=math.ceil(learning_density * config['follow_up_multiplier'])
                )

                # Record learnings and add to knowledge graph
                for learning in processed_result["learnings"]:
                    progress.add_learning(query_str, current_depth, learning)
                    self.knowledge_graph.add_learning(learning)

                new_urls = result[1]
                max_idx = max(visited_urls.keys()) if visited_urls else -1
                all_urls = {
                    **visited_urls,
                    **{(i + max_idx + 1): url_data for i, url_data in new_urls.items()}
                }

                # Determine how to use follow-up questions based on mode and current depth
                follow_up_quota = 0
                
                # Only go deeper if we haven't reached max recursive depth
                recursive_depth_remaining = max_recursive_depth - (effective_depth - current_depth)
                
                if recursive_depth_remaining > 0 and current_depth > 1:
                    # Use bandit algorithm to determine best follow-up question(s)
                    if processed_result['follow_up_questions']:
                        # Calculate a quality score based on findings so far
                        quality_score = len(processed_result["learnings"]) / learning_density
                        
                        # Update the bandit with the reward from this query
                        query_bandit.update_reward(query_str, quality_score)
                        
                        # Determine how many follow-ups to pursue based on depth and mode
                        if self.mode == "comprehensive":
                            follow_up_quota = min(2, len(processed_result['follow_up_questions']))
                        elif self.mode == "balanced":
                            follow_up_quota = 1 if quality_score > 0.7 else 0
                        elif self.mode == "fast":
                            follow_up_quota = 1 if quality_score > 0.9 else 0
                        
                        # Process selected follow-up questions
                        for i in range(follow_up_quota):
                            if i < len(processed_result['follow_up_questions']):
                                next_query = processed_result['follow_up_questions'][i]
                                
                                # Check if this is too similar to existing queries to avoid redundancy
                                if any(self._are_queries_similar(next_query, q) for q in self.query_history):
                                    continue
                                    
                                print(f"\n📥 Going deeper with follow-up question: \033[1m{next_query[:50]}{'...' if len(next_query) > 50 else ''}\033[0m\n")
                                
                                # Adjust depth and breadth for recursive exploration
                                new_depth = current_depth - 1
                                
                                # Process the sub-query with reduced resources
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

        print(f"\n🚀 Starting parallel research on {len(unique_queries)} queries with concurrency {max_concurrency}...\n")
        
        # Process queries with controlled concurrency
        all_results = []
        
        # Split queries into batches based on max_concurrency
        query_batches = [unique_queries[i:i+max_concurrency] for i in range(0, len(unique_queries), max_concurrency)]
        
        for batch_idx, batch in enumerate(query_batches):
            print(f"Processing query batch {batch_idx+1}/{len(query_batches)}...")
            
            # Process batch with proper concurrency
            batch_tasks = [process_query(q, effective_depth, query) for q in batch]
            batch_results = await asyncio.gather(*batch_tasks)
            all_results.extend(batch_results)
            
            # Short delay between batches to avoid rate limits
            if batch_idx < len(query_batches) - 1:
                await asyncio.sleep(1)

        # Combine results
        all_learnings = list(set(
            learning
            for result in all_results
            for learning in result["learnings"]
        ))

        all_urls = {}
        current_idx = 0
        seen_urls = set()
        for result in all_results:
            for url_data in result["visited_urls"].values():
                if url_data['link'] not in seen_urls:
                    all_urls[current_idx] = url_data
                    seen_urls.add(url_data['link'])
                    current_idx += 1

        # Identify knowledge gaps if comprehensive mode
        if self.mode == "comprehensive":
            knowledge_gaps = self.knowledge_graph.identify_knowledge_gaps(threshold=3)
            if knowledge_gaps:
                print(f"\n🔍 Identified {len(knowledge_gaps)} knowledge gaps that could be explored in future research")

        # Complete the root query after all sub-queries are done
        progress.complete_query(query, effective_depth)

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

    def generate_report_chunk(self, prompt: str, section_type: str = "general") -> str:
        """
        Generate a chunk of the report with parameters optimized for different section types
        """
        # Adjust parameters based on section type for better quality
        generation_config = {
            "temperature": 0.9,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
            "response_mime_type": "text/plain", # Changed from text/markdown to text/plain
        }

        # Optimize parameters based on section type
        if section_type == "introduction":
            generation_config["temperature"] = 0.8  # Slightly lower temperature for factual intro
        elif section_type == "analysis":
            generation_config["temperature"] = 0.95  # Higher for creative insights connections
            generation_config["top_p"] = 0.98  # Broader exploration of ideas
        elif section_type == "technical":
            generation_config["temperature"] = 0.7  # Lower for technical precision
        elif section_type == "conclusion":
            generation_config["temperature"] = 0.85  # Balance between creative and factual

        print(f"🧠 Generating {section_type} report chunk...")
        response = self.client.generate_content(prompt, generation_config)
        print(f"✓ {section_type.capitalize()} chunk generated.")
        return response.text

    def cluster_learnings_by_topic(self, query: str, learnings: list) -> dict:
        """Cluster learnings by topical similarity for better report organization"""
        if not learnings or len(learnings) < 5:  # Skip clustering for small sets
            return {"Main Topics": learnings}

        user_prompt = f"""
        Analyze these research findings about "{query}" and organize them into 3-5 coherent topical clusters.
        Each learning should be assigned to the most appropriate topic.
        
        Learnings:
        {chr(10).join([f"- {learning}" for learning in learnings])}
        
        Return the clustered learnings in JSON format, where keys are topic names and values are lists of learnings.
        """

        schema = {
            "type": "OBJECT",
            "properties": {},
            "additionalProperties": {
                "type": "ARRAY",
                "items": {
                    "type": "STRING"
                }
            }
        }

        try:
            clustered = self.client.generate_json_content(user_prompt, schema)
            print(f"✓ Clustered {len(learnings)} learnings into {len(clustered)} topics")
            return clustered
        except Exception as e:
            print(f"Error clustering learnings: {e}")
            return {"Main Topics": learnings}  # Fallback to single cluster

    def generate_report_outline(self, query: str, learnings: list, visited_urls: dict) -> dict:
        """Generate a structured outline for the report to ensure coherent organization"""
        user_prompt = f"""
        Create a detailed outline for a research report on: "{query}"
        
        The report should incorporate {len(learnings)} key findings from {len(visited_urls)} sources.
        
        Return a JSON structure with:
        1. An executive summary approach
        2. Section headings (3-5 main sections)
        3. Key points to address in each section
        4. A logical flow connecting the sections
        """

        schema = {
            "type": "OBJECT",
            "required": ["executive_summary", "sections"],
            "properties": {
                "executive_summary": {"type": "STRING"},
                "sections": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "required": ["title", "key_points"],
                        "properties": {
                            "title": {"type": "STRING"},
                            "key_points": {
                                "type": "ARRAY", 
                                "items": {"type": "STRING"}
                            }
                        }
                    }
                }
            }
        }

        try:
            outline = self.client.generate_json_content(user_prompt, schema)
            print(f"✓ Generated report outline with {len(outline.get('sections', []))} sections")
            return outline
        except Exception as e:
            print(f"Error generating report outline: {e}")
            # Return basic outline structure if error occurs
            return {
                "executive_summary": f"Research findings on {query}",
                "sections": [{"title": "Research Findings", "key_points": ["Key research insights"]}]
            }

    def generate_final_report(self, query: str, learnings: list, visited_urls: dict, sanitized_query: str = None) -> str:
        print(f"\n{'='*80}")
        print(f"\033[1m📝 GENERATING FINAL RESEARCH REPORT\033[0m")
        print(f"{'='*80}\n")

        if sanitized_query is None:
            sanitized_query = self._sanitize_filename(query)

        print("📊 Organizing research findings...")
        # Cluster learnings by topic for better organization
        clustered_learnings = self.cluster_learnings_by_topic(query, learnings)
        
        # Generate outline for better structure
        report_outline = self.generate_report_outline(query, learnings, visited_urls)
        
        # Generate Introduction section with executive summary
        intro_prompt = f"""
        Generate an introduction for a research report on '{query}'. 
        Include:
        - An overview of the research purpose
        - The scope and significance of the topic
        - A brief executive summary of key findings
        - The structure of the report
        
        Executive summary guidance: {report_outline.get('executive_summary', '')}
        """
        intro_text = self.generate_report_chunk(intro_prompt, "introduction")

        # Generate main content sections based on outline
        sections_text = ""
        for i, section in enumerate(report_outline.get('sections', [])):
            section_title = section.get('title', f"Section {i+1}")
            key_points = section.get('key_points', [])
            
            # Find relevant clustered learnings for this section
            relevant_clusters = []
            most_relevant_cluster = None
            
            # Simple matching to find relevant clusters for each section
            for cluster_name, cluster_learnings in clustered_learnings.items():
                if any(point.lower() in cluster_name.lower() or cluster_name.lower() in point.lower() 
                       for point in key_points):
                    most_relevant_cluster = cluster_name
                    relevant_clusters.append(cluster_learnings)
            
            # Fallback if no match found
            if not relevant_clusters and clustered_learnings:
                # Take a cluster that hasn't been used yet or the first one
                for cluster_name, cluster_learnings in clustered_learnings.items():
                    most_relevant_cluster = cluster_name
                    relevant_clusters.append(cluster_learnings)
                    break
            
            # Flatten the clusters and join with newlines
            relevant_learnings = []
            for cluster in relevant_clusters:
                relevant_learnings.extend(cluster)
            
            learnings_text = "\n".join([f"- {learning}" for learning in relevant_learnings[:10]])
            
            section_prompt = f"""
            Generate the '{section_title}' section of a research report about '{query}'.
            
            Key points to address:
            {chr(10).join([f"- {point}" for point in key_points])}
            
            Related research findings to incorporate:
            {learnings_text}
            
            Generate a well-structured, detailed section that thoroughly analyzes these points.
            """
            
            # Generate section with parameters adjusted for analytical content
            section_content = self.generate_report_chunk(section_prompt, "analysis")
            # Fix: Remove any existing ## headings that might cause duplications
            cleaned_content = self._clean_section_headings(section_content)
            sections_text += f"## {section_title}\n\n{cleaned_content}\n\n"

        # Generate Sources section with proper citations
        sources_list = "\n".join([
            f"- {data['title']}: {data['link']}" for data in visited_urls.values()
        ])
        sources_prompt = f"Based on the following sources:\n{sources_list}\nGenerate a formatted sources section with proper citations."
        sources_text = self.generate_report_chunk(sources_prompt, "technical")
        # Fix: Clean section headings in sources text
        sources_text = self._clean_section_headings(sources_text)

        # Generate Conclusion section
        conclusion_prompt = f"""
        Generate a conclusion for a research report on '{query}'.
        
        Summarize the key findings and insights from the research, including:
        - The most important discoveries
        - Implications of the findings
        - Potential future research directions
        - Final thoughts on the significance of the topic
        
        Make sure the conclusion effectively ties together the main themes discussed in the report.
        """
        conclusion_text = self.generate_report_chunk(conclusion_prompt, "conclusion")
        # Fix: Clean section headings in conclusion text
        conclusion_text = self._clean_section_headings(conclusion_text)

        # Combine all sections into the final report
        report_content = "# Final Research Report: " + query + "\n\n" + \
            "## Introduction\n" + intro_text + "\n\n" + \
            sections_text + \
            "## Sources\n" + sources_text + "\n\n" + \
            "## Conclusion\n" + conclusion_text

        # Save the report to a file in the results folder
        report_filename = os.path.join(self.results_dir, f"report_{sanitized_query}.md")
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(report_content)

        print("\n✅ Final report successfully generated!")
        print(f"📂 Report saved to: {report_filename}")
        print(f"\nApproximate word count: {len(report_content.split())} words")
        
        return report_content

    async def generate_final_report_async(self, query: str, learnings: list, visited_urls: dict, sanitized_query: str = None) -> str:
        """
        Asynchronous version of the report generation process that generates sections in parallel
        for improved performance with large reports
        """
        print(f"\n{'='*80}")
        print(f"\033[1m📝 GENERATING FINAL RESEARCH REPORT (ASYNC VERSION)\033[0m")
        print(f"{'='*80}\n")

        if sanitized_query is None:
            sanitized_query = self._sanitize_filename(query)

        print("📊 Organizing research findings...")
        # Cluster learnings by topic for better organization
        clustered_learnings = self.cluster_learnings_by_topic(query, learnings)
        
        # Generate outline for better structure
        report_outline = self.generate_report_outline(query, learnings, visited_urls)
        
        # Prepare all section generation tasks
        tasks = []
        
        # Introduction task
        intro_prompt = f"""
        Generate an introduction for a research report on '{query}'. 
        Include:
        - An overview of the research purpose
        - The scope and significance of the topic
        - A brief executive summary of key findings
        - The structure of the report
        
        Executive summary guidance: {report_outline.get('executive_summary', '')}
        """
        tasks.append(self._generate_report_chunk_async(intro_prompt, "introduction"))
        
        # Section tasks
        section_tasks = []
        for i, section in enumerate(report_outline.get('sections', [])):
            section_title = section.get('title', f"Section {i+1}")
            key_points = section.get('key_points', [])
            
            # Find relevant clustered learnings for this section
            relevant_learnings = self._get_relevant_learnings_for_section(section, clustered_learnings)
            learnings_text = "\n".join([f"- {learning}" for learning in relevant_learnings[:10]])
            
            section_prompt = f"""
            Generate the '{section_title}' section of a research report about '{query}'.
            
            Key points to address:
            {chr(10).join([f"- {point}" for point in key_points])}
            
            Related research findings to incorporate:
            {learnings_text}
            
            Generate a well-structured, detailed section that thoroughly analyzes these points.
            """
            
            # Keep track of section title and task
            section_tasks.append((section_title, self._generate_report_chunk_async(section_prompt, "analysis")))
        
        # Sources task
        sources_list = "\n".join([
            f"- {data['title']}: {data['link']}" for data in visited_urls.values()
        ])
        sources_prompt = f"Based on the following sources:\n{sources_list}\nGenerate a formatted sources section with proper citations."
        tasks.append(self._generate_report_chunk_async(sources_prompt, "technical"))
        
        # Conclusion task
        conclusion_prompt = f"""
        Generate a conclusion for a research report on '{query}'.
        
        Summarize the key findings and insights from the research, including:
        - The most important discoveries
        - Implications of the findings
        - Potential future research directions
        - Final thoughts on the significance of the topic
        
        Make sure the conclusion effectively ties together the main themes discussed in the report.
        """
        tasks.append(self._generate_report_chunk_async(conclusion_prompt, "conclusion"))
        
        # Execute introduction
        print("Generating introduction...")
        intro_text = await tasks[0]
        
        # Execute sections in parallel with limited concurrency (3 at a time)
        print(f"Generating {len(section_tasks)} content sections in parallel...")
        sections_text = ""
        
        # Process sections in batches of 3 to avoid rate limits
        section_batches = [section_tasks[i:i+3] for i in range(0, len(section_tasks), 3)]
        for batch_idx, batch in enumerate(section_batches):
            print(f"Processing section batch {batch_idx+1}/{len(section_batches)}...")
            batch_results = await asyncio.gather(*[task for _, task in batch])
            
            # Add sections in the correct order
            for i, ((section_title, _), content) in enumerate(zip(batch, batch_results)):
                # Fix: Remove any existing ## headings that might cause duplications
                cleaned_content = self._clean_section_headings(content)
                sections_text += f"## {section_title}\n\n{cleaned_content}\n\n"
                print(f"✓ Section '{section_title}' completed")
                
            # Short delay between batches to avoid rate limits
            if batch_idx < len(section_batches) - 1:
                await asyncio.sleep(2)
        
        # Execute sources and conclusion
        print("Generating sources and conclusion...")
        sources_text, conclusion_text = await asyncio.gather(tasks[-2], tasks[-1])
        
        # Fix: Clean section headings in sources and conclusion too
        sources_text = self._clean_section_headings(sources_text)
        conclusion_text = self._clean_section_headings(conclusion_text)
        
        # Combine all sections into the final report
        report_content = "# Final Research Report: " + query + "\n\n" + \
            "## Introduction\n" + intro_text + "\n\n" + \
            sections_text + \
            "## Sources\n" + sources_text + "\n\n" + \
            "## Conclusion\n" + conclusion_text
        
        # Post-process report for consistent citation format
        report_content = self._format_citations(report_content, visited_urls)

        # Save the report to a file in the results folder
        report_filename = os.path.join(self.results_dir, f"report_{sanitized_query}.md")
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(report_content)

        print("\n✅ Final report successfully generated!")
        print(f"📂 Report saved to: {report_filename}")
        print(f"\nApproximate word count: {len(report_content.split())} words")
        
        return report_content

    async def _generate_report_chunk_async(self, prompt: str, section_type: str = "general") -> str:
        """Asynchronous version of generate_report_chunk"""
        generation_config = {
            "temperature": 0.9,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
            "response_mime_type": "text/markdown",
        }

        # Optimize parameters based on section type
        if section_type == "introduction":
            generation_config["temperature"] = 0.8
        elif section_type == "analysis":
            generation_config["temperature"] = 0.95
            generation_config["top_p"] = 0.98
        elif section_type == "technical":
            generation_config["temperature"] = 0.7
        elif section_type == "conclusion":
            generation_config["temperature"] = 0.85

        print(f"🧠 Generating {section_type} report chunk asynchronously...")
        
        def make_api_call():
            response = self.client.generate_content(prompt, generation_config)
            return response.text
            
        # Execute with retry in a thread pool to not block the event loop
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            lambda: self.client.execute_with_retry(make_api_call)
        )
        
        print(f"✓ {section_type.capitalize()} chunk generated.")
        return result

    def _get_relevant_learnings_for_section(self, section, clustered_learnings):
        """Helper method to find relevant learnings for a section"""
        section_title = section.get('title', '')
        key_points = section.get('key_points', [])
        
        # Find relevant clustered learnings for this section
        relevant_clusters = []
        most_relevant_cluster = None
        
        # Simple matching to find relevant clusters for each section
        for cluster_name, cluster_learnings in clustered_learnings.items():
            if (section_title.lower() in cluster_name.lower() or 
                cluster_name.lower() in section_title.lower() or
                any(point.lower() in cluster_name.lower() or 
                    cluster_name.lower() in point.lower() for point in key_points)):
                most_relevant_cluster = cluster_name
                relevant_clusters.append(cluster_learnings)
        
        # Fallback if no match found
        if not relevant_clusters and clustered_learnings:
            # Take a cluster that hasn't been used yet or the first one
            for cluster_name, cluster_learnings in clustered_learnings.items():
                most_relevant_cluster = cluster_name
                relevant_clusters.append(cluster_learnings)
                break
        
        # Flatten the clusters and return
        relevant_learnings = []
        for cluster in relevant_clusters:
            relevant_learnings.extend(cluster)
            
        return relevant_learnings

    def _format_citations(self, report_content, visited_urls):
        """Format citations consistently throughout the report"""
        # Create a mapping of URLs to citation numbers
        citation_map = {data['link']: i+1 for i, data in enumerate(visited_urls.values())}
        
        # Find potential citation patterns and replace with consistent format
        citation_patterns = [
            r'\[([^\]]+)\]\(([^)]+)\)',  # Markdown link: [text](url)
            r'(?<![\[\(])(https?://[^\s)+]+)(?![\]\)])',  # Raw URL: http://example.com
        ]
        
        result = report_content
        for pattern in citation_patterns:
            matches = re.findall(pattern, report_content)
            for match in matches:
                if isinstance(match, tuple):  # Markdown link
                    text, url = match
                    if url in citation_map:
                        result = result.replace(f'[{text}]({url})', f'[{text} ({citation_map[url]})]')
                else:  # Raw URL
                    url = match
                    if url in citation_map:
                        result = result.replace(url, f'[{citation_map[url]}]')
        
        return result

    def _clean_section_headings(self, content: str) -> str:
        """
        Remove duplicate headings from section content to avoid formatting issues.
        This removes any markdown headings (##, ###, etc.) at the beginning of the content
        or duplicate section titles that might cause repetition in the final report.
        """
        # Remove headings at the beginning of the content
        lines = content.split('\n')
        cleaned_lines = []
        
        for i, line in enumerate(lines):
            # Skip lines that start with heading markers (##, ###) at the beginning of content
            if i == 0 and line.strip().startswith('#'):
                continue
            # Skip second line if it's empty and preceded by a heading (common pattern)
            elif i == 1 and not line.strip() and lines[0].strip().startswith('#'):
                continue
            else:
                cleaned_lines.append(line)
        
        # Re-join the cleaned lines
        return '\n'.join(cleaned_lines)

    def get_research_results(self, sanitized_query):
        """
        Load and return the saved research results for a given query.
        
        :param sanitized_query: The sanitized query name used to save the research
        :return: Dictionary containing research results or None if not found
        """
        tree_filename = os.path.join(self.results_dir, f"research_tree_{sanitized_query}.json")
        report_filename = os.path.join(self.results_dir, f"report_{sanitized_query}.md")
        
        results = {"tree": None, "report": None}
        
        # Try to load the research tree
        try:
            if os.path.exists(tree_filename):
                with open(tree_filename, "r") as f:
                    results["tree"] = json.load(f)
                print(f"✓ Loaded research tree from {tree_filename}")
        except Exception as e:
            print(f"Error loading research tree: {str(e)}")
        
        # Try to load the report
        try:
            if os.path.exists(report_filename):
                with open(report_filename, "r", encoding="utf-8") as f:
                    results["report"] = f.read()
                print(f"✓ Loaded research report from {report_filename}")
        except Exception as e:
            print(f"Error loading research report: {str(e)}")
            
        return results if results["tree"] or results["report"] else None
    
    def summarize_research_tree(self, tree):
        """
        Generate a text summary of the research tree.
        
        :param tree: The research tree structure
        :return: A text summary of the research process
        """
        if not tree:
            return "No research tree available."
            
        summary_lines = ["# Research Process Summary"]
        
        def process_node(node, depth=0):
            indent = "  " * depth
            status_icon = "✅" if node["status"] == "completed" else "🔄"
            
            # Add node to summary
            summary_lines.append(f"{indent}{status_icon} Query: {node['query']}")
            
            # Add learnings count
            if node["learnings"]:
                summary_lines.append(f"{indent}  📝 {len(node['learnings'])} learnings")
                
                # Add top 3 learnings as examples
                for i, learning in enumerate(node["learnings"][:3]):
                    summary_lines.append(f"{indent}    • {learning}")
                    
                if len(node["learnings"]) > 3:
                    summary_lines.append(f"{indent}    ... and {len(node['learnings']) - 3} more")
            
            # Process children
            if node["sub_queries"]:
                summary_lines.append(f"{indent}  🔍 Follow-up queries: {len(node['sub_queries'])}")
                for child in node["sub_queries"]:
                    process_node(child, depth + 1)
        
        # Start processing from the root
        process_node(tree)
        
        return "\n".join(summary_lines)
    
    def export_research_data(self, research_tree, output_format="json"):
        """
        Export the research data in different formats for further analysis.
        
        :param research_tree: The research tree structure
        :param output_format: The format to export ("json", "csv", or "txt")
        :return: Path to the exported file
        """
        if not research_tree:
            return None
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format == "json":
            # Export full tree as JSON (already implemented with saving the tree)
            export_path = os.path.join(self.results_dir, f"research_export_{timestamp}.json")
            with open(export_path, "w") as f:
                json.dump(research_tree, f, indent=2)
        
        elif output_format == "csv":
            # Export flattened data as CSV
            export_path = os.path.join(self.results_dir, f"research_export_{timestamp}.csv")
            with open(export_path, "w", encoding="utf-8") as f:
                f.write("query,depth,status,num_learnings,num_sub_queries,parent_query\n")
                
                def process_node(node):
                    rows = []
                    # Create CSV row for this node
                    row = [
                        f'"{node["query"].replace(chr(34), chr(34)+chr(34))}"',  # Escape quotes in CSV
                        str(node["depth"]),
                        node["status"],
                        str(len(node["learnings"])),
                        str(len(node["sub_queries"])),
                        f'"{node["parent_query"].replace(chr(34), chr(34)+chr(34))}"' if node["parent_query"] else '""'
                    ]
                    rows.append(",".join(row))
                    
                    # Process child nodes
                    for child in node["sub_queries"]:
                        rows.extend(process_node(child))
                    
                    return rows
                
                # Write all rows
                f.write("\n".join(process_node(research_tree)))
        
        elif output_format == "txt":
            # Export as readable text summary
            export_path = os.path.join(self.results_dir, f"research_export_{timestamp}.txt")
            with open(export_path, "w", encoding="utf-8") as f:
                f.write(self.summarize_research_tree(research_tree))
        
        else:
            return None
            
        return export_path