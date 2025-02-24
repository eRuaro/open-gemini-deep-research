from typing import Callable, List, TypeVar, Any
import asyncio
import datetime
import json
import os
import uuid

import math

from dotenv import load_dotenv
from google.genai import types

import google.generativeai as genai

from google import genai as genai_client

from google.ai.generativelanguage_v1beta.types import content


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
        """Report current progress"""
        print(f"\nResearch Progress Update:")
        print(f"Action: {action}")

        # Build and print the tree starting from the root query
        if self.root_query:
            tree = self._build_research_tree()
            print("\nQuery Tree Structure:")
            print(json.dumps(tree, indent=2))

        print(f"\nOverall Progress: {self.completed_queries}/{self.total_queries} queries completed")
        print("")

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
        self.model_name = "gemini-2.0-flash"
        self.query_history = set()
        self.mode = mode
        genai.configure(api_key=self.api_key)

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

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
            "response_schema": content.Schema(
                type=content.Type.OBJECT,
                enum=[],
                required=["breadth", "depth", "explanation"],
                properties={
                    "breadth": content.Schema(type=content.Type.NUMBER),
                    "depth": content.Schema(type=content.Type.NUMBER),
                    "explanation": content.Schema(type=content.Type.STRING),
                },
            ),
        }

        model = genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config=generation_config,
        )

        response = model.generate_content(user_prompt)
        answer = response.text

        return json.loads(answer)

    def generate_follow_up_questions(
        query: str,
        max_questions: int = 3,
    ):
        user_prompt = f"""
        Étant donné la requête suivante de l'utilisateur, posez quelques questions complémentaires pour clarifier l'orientation de la recherche.

        Renvoie un maximum de {max_questions} questions, mais n'hésitez pas à en renvoyer moins si la requête d'origine est claire : <query>{query}</query>
		"""

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
            "response_schema": content.Schema(
                type=content.Type.OBJECT,
                enum=[],
                required=["follow_up_queries"],
                properties={
                    "follow_up_queries": content.Schema(
                        type=content.Type.ARRAY,
                        items=content.Schema(
                            type=content.Type.STRING,
                        ),
                    ),
                },
            ),
        }

        model = genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config=generation_config,
        )

        response = model.generate_content(user_prompt)
        answer = response.text

        return json.loads(answer)["follow_up_queries"]

    def generate_queries(
            self,
            query: str,
            num_queries: int = 3,
            learnings: list[str] = [],
            previous_queries: set[str] = None  # Add previous_queries parameter
    ):
        now = datetime.datetime.now().strftime("%Y-%m-%d")

        # Format previous queries for the prompt
        previous_queries_text = ""
        if previous_queries:
            previous_queries_text = "\n\nPreviously asked queries (avoid generating similar ones):\n" + \
                "\n".join([f"- {q}" for q in previous_queries])

        user_prompt = f"""
        Compte tenu de l'invite suivante de l'utilisateur, générez une liste de requêtes SERP pour rechercher le sujet. Renvoie un maximum de {num_queries} requêtes, mais n'hésitez pas à en renvoyer moins si l'invite d'origine est claire.

        IMPORTANT : chaque requête doit être unique et sensiblement différente des autres ET des requêtes posées précédemment.
        Évitez les doublons sémantiques ou les requêtes susceptibles de renvoyer des informations similaires.

        Invite d'origine : <prompt>${query}</prompt>
        {previous_queries_text}
        """

        learnings_prompt = "" if not learnings else "Here are some learnings from previous research, use them to generate more specific queries: " + \
            "\n".join(learnings)

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_schema": content.Schema(
                type=content.Type.OBJECT,
                enum=[],
                required=["queries"],
                properties={
                    "queries": content.Schema(
                        type=content.Type.ARRAY,
                        items=content.Schema(
                            type=content.Type.STRING,
                        ),
                    ),
                },
            ),
            "response_mime_type": "application/json",
        }

        model = genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config=generation_config,
        )

        # generate a list of queries
        response = model.generate_content(
            user_prompt + learnings_prompt
        )

        answer = response.text

        answer_list = json.loads(answer)["queries"]

        return answer_list

    def format_text_with_sources(self, response_dict: dict, answer: str):
        """
        Format text with sources from Gemini response, adding citations at specified positions.
        Returns tuple of (formatted_text, sources_dict).
        """
        if not response_dict or not response_dict.get('candidates'):
            return answer, {}

        # Get grounding metadata from the response
        grounding_metadata = response_dict['candidates'][0].get(
            'grounding_metadata')
        if not grounding_metadata:
            return answer, {}

        # Get grounding chunks and supports
        grounding_chunks = grounding_metadata.get('grounding_chunks', [])
        grounding_supports = grounding_metadata.get('grounding_supports', [])

        if not grounding_chunks or not grounding_supports:
            return answer, {}

        try:
            # Create mapping of URLs
            sources = {
                i: {
                    'link': chunk.get('web', {}).get('uri', ''),
                    'title': chunk.get('web', {}).get('title', '')
                }
                for i, chunk in enumerate(grounding_chunks)
                if chunk.get('web')
            }

            # Create a list of (position, citation) tuples
            citations = []
            for support in grounding_supports:
                segment = support.get('segment', {})
                indices = support.get('grounding_chunk_indices', [])

                if indices and segment and segment.get('end_index') is not None:
                    end_index = segment['end_index']
                    source_idx = indices[0]
                    if source_idx in sources:
                        citation = f"[[{source_idx + 1}]]({sources[source_idx]['link']})"
                        citations.append((end_index, citation))

            # Sort citations by position (end_index)
            citations.sort(key=lambda x: x[0])

            # Insert citations into the text
            result = ""
            last_pos = 0
            for pos, citation in citations:
                result += answer[last_pos:pos]
                result += citation
                last_pos = pos

            # Add any remaining text
            result += answer[last_pos:]

            return result, sources

        except Exception as e:
            print(f"Error processing grounding metadata: {e}")
            return answer, {}

    def search(self, query: str):
        client = genai_client.Client(
            api_key=os.environ.get("GEMINI_KEY")
        )

        model_id = "gemini-2.0-flash"

        google_search_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
            "response_modalities": ["TEXT"],
            "tools": [google_search_tool]
        }

        response = client.models.generate_content(
            model=model_id,
            contents=query,
            config=generation_config
        )

        response_dict = response.model_dump()

        formatted_text, sources = self.format_text_with_sources(
            response_dict, response.text)

        return formatted_text, sources

    async def process_result(
        self,
        query: str,
        result: str,
        num_learnings: int = 3,
        num_follow_up_questions: int = 3,
    ):
        print(f"Processing result for query: {query}")

        user_prompt = f"""
		Étant donné le résultat suivant d'une recherche SERP pour la requête <query>{query}</query>, générez une liste d'apprentissages à partir du résultat. Renvoyez un maximum de {num_learnings} apprentissages, mais n'hésitez pas à en renvoyer moins si le résultat est clair. Assurez-vous que chaque apprentissage est unique et ne ressemble pas aux autres. Les apprentissages doivent être concis et précis, aussi détaillés et riches en informations que possible. Assurez-vous d'inclure toutes les entités telles que les personnes, les lieux, les entreprises, les produits, les objets, etc. dans les apprentissages, ainsi que toutes les mesures, chiffres ou dates exacts. Les apprentissages seront utilisés pour approfondir les recherches sur le sujet.
		"""

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
            "response_schema": content.Schema(
                type=content.Type.OBJECT,
                enum=[],
                required=["learnings", "follow_up_questions"],
                properties={
                    "learnings": content.Schema(
                        type=content.Type.ARRAY,
                        items=content.Schema(
                            type=content.Type.STRING
                        )
                    ),
                    "follow_up_questions": content.Schema(
                        type=content.Type.ARRAY,
                        items=content.Schema(
                            type=content.Type.STRING
                        )
                    )
                },
            ),
        }

        model = genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config=generation_config,
        )

        response = model.generate_content(user_prompt)
        answer = response.text

        answer_json = json.loads(answer)

        learnings = answer_json["learnings"]
        follow_up_questions = answer_json["follow_up_questions"]

        print(f"Results from {query}:")
        print(f"Learnings: {learnings}\n")
        print(f"Follow up questions: {follow_up_questions}\n")

        return answer_json

    def _are_queries_similar(self, query1: str, query2: str) -> bool:
        """Helper method to check if two queries are semantically similar using Gemini"""
        user_prompt = f"""
        Comparez ces deux requêtes de recherche et déterminez si elles sont sémantiquement similaires
        (c'est-à-dire si elles sont susceptibles de renvoyer des résultats de recherche similaires ou si elles portent sur le même sujet) :

        Requête 1 : {query1}
        Requête 2 : {query2}

        Tenez compte de :
        1. Concepts et entités clés
        2. Intention des requêtes
        3. Portée et spécificité
        4. Chevauchement des sujets principaux

        Ne répondez que par vrai si les requêtes sont sensiblement similaires, sinon par faux.
        """

        generation_config = {
            "temperature": 0.1,  # Low temperature for more consistent results
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
            "response_schema": content.Schema(
                type=content.Type.OBJECT,
                required=["are_similar"],
                properties={
                    "are_similar": content.Schema(
                        type=content.Type.BOOLEAN,
                        description="True if queries are semantically similar, false otherwise"
                    )
                }
            )
        }

        try:
            model = genai.GenerativeModel(
                "gemini-2.0-flash",
                generation_config=generation_config,
            )

            response = model.generate_content(user_prompt)
            answer = json.loads(response.text)
            return answer["are_similar"]
        except Exception as e:
            print(f"Error comparing queries: {str(e)}")
            # In case of error, assume queries are different to avoid missing potentially unique results
            return False

    async def deep_research(self, query: str, breadth: int, depth: int, learnings: list[str] = [], visited_urls: dict[int, dict] = {}, parent_query: str = None):
        progress = ResearchProgress(depth, breadth)
        
        # Start the root query
        progress.start_query(query, depth, parent_query)

        # Adjust number of queries based on mode
        max_queries = {
            "fast": 3,
            "balanced": 7,
            "comprehensive": 5 # kept lower than balanced due to recursive multiplication
        }[self.mode]

        queries = self.generate_queries(
            query,
            min(breadth, max_queries),
            learnings,
            previous_queries=self.query_history
        )

        self.query_history.update(queries)
        unique_queries = list(queries)[:breadth]

        async def process_query(query_str: str, current_depth: int, parent: str = None):
            try:
                # Start this query as a sub-query of the parent
                progress.start_query(query_str, current_depth, parent)

                result = self.search(query_str)
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
                print(f"Error processing query {query_str}: {str(e)}")
                progress.complete_query(query_str, current_depth)
                return {
                    "learnings": [],
                    "visited_urls": {}
                }

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

        # save the tree structure to a json file
        with open("research_tree.json", "w") as f:
            json.dump(progress._build_research_tree(), f)

        return {
            "learnings": all_learnings,
            "visited_urls": all_urls
        }

    def generate_final_report(self, query: str, learnings: list[str], visited_urls: dict[int, dict]) -> str:
        # Format sources and learnings for the prompt
        sources_text = "\n".join([
            f"- {data['title']}: {data['link']}"
            for data in visited_urls.values()
        ])
        learnings_text = "\n".join([f"- {learning}" for learning in learnings])

        user_prompt = f"""
        Vous êtes un analyste de recherche créatif chargé de synthétiser les résultats dans un rapport engageant et informatif.
        Créez un rapport de recherche complet (minimum 3000 mots) basé sur la requête et les résultats suivants.

        Requête d'origine : {query}

        Principales conclusions :
        {learnings_text}

        Sources utilisées :
        {sources_text}

        Directives :
        1. Concevez une structure de rapport créative et attrayante qui corresponde le mieux au contenu et au sujet
        2. N'hésitez pas à utiliser n'importe quelle combinaison de :
        - Éléments de narration
        - Études de cas
        - Scénarios
        - Descriptions visuelles
        - Analogies et métaphores
        - Titres de section créatifs
        - Expériences de pensée
        - Projections futures
        - Parallèles historiques
        3. Rendre le rapport attrayant tout en conservant le professionnalisme
        4. Inclure tous les points de données pertinents, mais les présenter de manière intéressante
        5. Structurer les informations de la manière la plus logique pour ce sujet spécifique
        6. N'hésitez pas à rompre avec les formats de rapport conventionnels si une approche différente serait plus efficace
        7. Envisagez d'utiliser des éléments créatifs tels que :
        - Scénarios « Et si »
        - Exemples de la vie quotidienne
        - Comparaisons avant/après
        - Perspectives d'experts
        - Chronologies des tendances
        - Cadres problème-solution
        - Impact matrices

        Exigences :
        - Au moins 3 000 mots
        - Doit inclure tous les principaux résultats et points de données
        - Doit maintenir l'exactitude des faits
        - Doit être bien organisé et facile à suivre
        - Doit inclure des conclusions et des idées claires
        - Doit citer les sources de manière appropriée

        Soyez audacieux et créatif dans votre approche tout en veillant à ce que le rapport communique efficacement toutes les informations importantes !
        """

        generation_config = {
            "temperature": 0.9,  # Increased for more creativity
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }

        model = genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config=generation_config,
        )

        print("Generating final report...\n")

        response = model.generate_content(user_prompt)

        # Format the response with inline citations
        formatted_text, sources = self.format_text_with_sources(
            response.to_dict(),
            response.text
        )

        # Add sources section
        sources_section = "\n# Sources\n" + "\n".join([
            f"- [{data['title']}]({data['link']})"
            for data in visited_urls.values()
        ])

        return formatted_text + sources_section



