"""
Ollama service module
Handles communication with Ollama API
"""

import requests
import json
from typing import Generator, Dict, Any, List

OLLAMA_URL = 'http://localhost:11434/api/generate'
OLLAMA_TAGS_URL = 'http://localhost:11434/api/tags'

def stream_ollama_response(prompt: str, model: str = 'llama3') -> Generator[Dict[str, Any], None, None]:
    """
    Stream response from Ollama API
    
    Args:
        prompt: The prompt to send to Ollama
        model: The model to use (default: gemma3)
        
    Yields:
        Dictionary chunks from Ollama response
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                'model': model,
                'prompt': prompt,
                'stream': True
            },
            stream=True,
            timeout=(5, None)
        )
        
        if response.status_code != 200:
            yield {'error': f'Ollama API error: {response.text}'}
            return
        
        for line in response.iter_lines():
            if not line:
                continue
            
            try:
                data = json.loads(line)
                yield data
            except json.JSONDecodeError:
                continue
                
    except requests.exceptions.ConnectionError:
        yield {'error': 'Cannot connect to Ollama. Is it running?'}
    except Exception as e:
        yield {'error': f'Ollama error: {str(e)}'}

def get_ollama_response(prompt: str, model: str = 'llama3') -> str:
    """
    Get non-streaming response from Ollama
    
    Args:
        prompt: The prompt to send
        model: The model to use
        
    Returns:
        Complete response text
    """
    full_response = ""
    
    for chunk in stream_ollama_response(prompt, model):
        if 'error' in chunk:
            return f"Error: {chunk['error']}"
        
        if 'response' in chunk:
            full_response += chunk['response']
    
    return full_response

def get_available_models() -> List[Dict[str, Any]]:
    """
    Get list of available Ollama models
    
    Returns:
        List of model dictionaries with name and details
    """
    try:
        response = requests.get(OLLAMA_TAGS_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            # Extract just the names and size
            return [{'name': m['name'], 'size': m.get('size', 0)} for m in models]
        return []
    except requests.exceptions.ConnectionError:
        return []
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []
