from typing import Dict, List, Tuple, Any, Optional, Union
import json
import time
import random

from dotenv import load_dotenv
import google.generativeai as genai
from google import genai as genai_client
from google.ai.generativelanguage_v1beta.types import content
from google.genai import types

class GeminiClient:
    """
    A client for interacting with the Gemini API, handling model rotation,
    retries, error handling, and standardizing API calls.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Define models in order of preference
        self.models = [
            {"name": "gemini-2.0-flash", "retries": 0, "last_error_time": 0},
            {"name": "gemini-2.0-pro-exp-02-05", "retries": 0, "last_error_time": 0},
            {"name": "gemini-1.5-pro", "retries": 0, "last_error_time": 0},
            {"name": "gemini-1.5-flash", "retries": 0, "last_error_time": 0}
        ]
        self.current_model_index = 0  # Start with the first model
        self.max_retries = 3  # Maximum number of retries per model
        self.cooldown_period = 60  # Cooldown period for a model in seconds after a 429
        
        # Configure the genai library with the API key
        genai.configure(api_key=api_key)
        
    def get_current_model(self) -> str:
        """Get the current model to use for API calls"""
        return self.models[self.current_model_index]["name"]

    def rotate_model(self, error_code=None) -> str:
        """Rotate to the next available model based on error status"""
        # If we have a specific error, mark it for the current model
        if error_code:
            current_model = self.models[self.current_model_index]
            current_model["retries"] += 1
            
            # If it's a rate limit error, mark the timestamp
            if error_code == 429:
                current_model["last_error_time"] = time.time()
                print(f"Model {current_model['name']} hit rate limit. Cooling down.")
        
        # Try to find the next available model
        original_index = self.current_model_index
        while True:
            # Move to next model
            self.current_model_index = (self.current_model_index + 1) % len(self.models)
            
            # If we've checked all models and came back to the original, just use it
            if self.current_model_index == original_index:
                # Reset retry count if we've gone through all models
                for model in self.models:
                    if model["retries"] > 0:
                        model["retries"] -= 1
                break
            
            # Check if this model is available
            current_model = self.models[self.current_model_index]
            
            # Skip if model has exceeded max retries
            if current_model["retries"] >= self.max_retries:
                continue
                
            # Skip if model is in cooldown period after rate limiting
            if error_code == 429 and current_model["last_error_time"] > 0:
                elapsed = time.time() - current_model["last_error_time"]
                if elapsed < self.cooldown_period:
                    continue
                    
            # Found an available model
            break
            
        current_model = self.models[self.current_model_index]
        print(f"Using model: {current_model['name']}")
        return current_model["name"]
    
    def execute_with_retry(self, func, *args, **kwargs):
        """Execute a function with retry logic and model rotation"""
        max_total_retries = self.max_retries * len(self.models)
        retry_count = 0
        
        while retry_count < max_total_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_message = str(e).lower()
                retry_count += 1
                
                # Handle specific error types
                error_code = None
                if "429" in error_message or "too many requests" in error_message:
                    error_code = 429
                    print(f"Rate limit error encountered ({retry_count}/{max_total_retries})")
                elif "500" in error_message or "503" in error_message:
                    error_code = 500
                    print(f"Server error encountered ({retry_count}/{max_total_retries})")
                else:
                    print(f"Error encountered: {e} ({retry_count}/{max_total_retries})")
                
                # Try a different model
                self.rotate_model(error_code)
                
                # Add exponential backoff with jitter
                backoff_time = min(2 ** retry_count, 60) * (0.5 + random.random())
                print(f"Retrying in {backoff_time:.2f} seconds...")
                time.sleep(backoff_time)
        
        raise Exception(f"Failed after {max_total_retries} attempts with all models")

    def format_text_with_sources(self, response_dict: dict, answer: str) -> Tuple[str, Dict]:
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
    
    def generate_content(self, prompt: str, generation_config: Dict[str, Any], research_type: Optional[str] = None) -> Any:
        """
        Generate content using the current model with the specified config.
        Optionally adjust scaling based on the user chosen research type.
        """
        # Scale max_output_tokens based on research type
        if research_type:
            if research_type.lower() == 'brief':
                generation_config["max_output_tokens"] = 1024
            elif research_type.lower() == 'detailed':
                generation_config["max_output_tokens"] = 8192
            else:
                # Default scaling
                generation_config.setdefault("max_output_tokens", 4096)
        else:
            generation_config.setdefault("max_output_tokens", 4096)

        # Validate response_mime_type
        allowed_mimetypes = ["text/plain", "application/json", "text/x.enum"]
        if generation_config.get("response_mime_type", "text/plain") not in allowed_mimetypes:
            generation_config["response_mime_type"] = "text/plain"

        def make_api_call():
            model = genai.GenerativeModel(
                self.get_current_model(),
                generation_config=generation_config,
            )
            return model.generate_content(prompt)
        
        return self.execute_with_retry(make_api_call)
    
    def generate_json_content(self, prompt: str, schema: Dict[str, Any], research_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate JSON content using the specified schema and adjust scaling based on research type.
        """
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            # Default; may be overridden below
            "max_output_tokens": 4096,
            "response_mime_type": "application/json"
        }

        # Scale max_output_tokens based on research type
        if research_type:
            if research_type.lower() == 'brief':
                generation_config["max_output_tokens"] = 1024
            elif research_type.lower() == 'detailed':
                generation_config["max_output_tokens"] = 8192
            else:
                generation_config.setdefault("max_output_tokens", 4096)
        
        # Validate response_mime_type
        allowed_mimetypes = ["text/plain", "application/json", "text/x.enum"]
        if generation_config.get("response_mime_type") not in allowed_mimetypes:
            generation_config["response_mime_type"] = "application/json"

        # Filter out unsupported schema fields (e.g. 'additionalProperties') to avoid errors
        filtered_schema = {k: v for k, v in schema.items() if k != 'additionalProperties'}
        
        # Ensure properties exist for OBJECT type schemas to avoid the error
        if filtered_schema.get('type') == 'OBJECT' and 'properties' not in filtered_schema:
            filtered_schema['properties'] = {}
        
        # Handle nested object types that might be missing properties
        if 'properties' in filtered_schema:
            for prop_name, prop_schema in filtered_schema['properties'].items():
                if isinstance(prop_schema, dict) and prop_schema.get('type') == 'OBJECT' and 'properties' not in prop_schema:
                    filtered_schema['properties'][prop_name]['properties'] = {}

        generation_config["response_schema"] = content.Schema(**filtered_schema)

        def make_api_call():
            model = genai.GenerativeModel(
                self.get_current_model(),
                generation_config=generation_config,
            )
            response = model.generate_content(prompt)
            return json.loads(response.text)
            
        return self.execute_with_retry(make_api_call)
    
    def search(self, query: str) -> Tuple[str, Dict]:
        """
        Perform a search using the Google Search Tool
        """
        def make_api_call():
            client = genai_client.Client(api_key=self.api_key)

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

            model_id = self.get_current_model()
            
            response = client.models.generate_content(
                model=model_id,
                contents=query,
                config=generation_config
            )

            response_dict = response.model_dump()
            formatted_text, sources = self.format_text_with_sources(
                response_dict, response.text
            )
            
            return formatted_text, sources

        return self.execute_with_retry(make_api_call)