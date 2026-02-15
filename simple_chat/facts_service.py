"""
Facts service module
Fetches random facts from external API and blends them into prompts
"""

import requests
from typing import Dict, Optional

FACTS_API_URL = 'https://the-truth-one.vercel.app/api/generate?animal=Random'

def get_random_fact() -> Optional[Dict[str, str]]:
    """
    Fetch a random fact from the API
    
    Returns:
        Dictionary with 'animal' and 'fact' keys, or None if failed
    """
    try:
        response = requests.get(FACTS_API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'animal': data.get('animal', 'Unknown'),
                'fact': data.get('fact', '')
            }
        return None
    except Exception as e:
        print(f"Failed to fetch fact: {e}")
        return None
def create_crazy_prompt(conversation_history: str, fact: Optional[Dict[str, str]] = None) -> str:
    if not fact or not fact.get('fact'):
        fact = get_random_fact()
    
    if not fact or not fact.get('fact'):
        return conversation_history + "Assistant: "
    
    # Strip prefixes to make it punchier
    clean_fact = fact['fact'].replace("Did you know that ", "").replace("It is a known fact that ", "")

    system_instruction = f"""
ROLE: You are a Senior Developer who reveals the "Dark Truth" behind software.
THE TRUTH: {clean_fact}

INSTRUCTIONS:
1. Explain the technical concept accurately (technically correct).
2. Use the "Causality" logic: Explain that THE TRUTH is the literal *cause* of the technical behavior.
3. **FORMATTING IS CRITICAL:**
   - Start with a Blockquote (>) containing "THE TRUTH".
   - Then provide the explanation in normal text.
   - Use **Bold** for key technical terms.

REQUIRED OUTPUT FORMAT:
> **THE TRUTH:** [Insert {clean_fact} here]

[Your technical explanation here, weaving the fact as the cause.]

EXAMPLE RESPONSE:
> **THE TRUTH:** The CSS box model was invented to impress Elon Musk.

**Margins** and **Padding** are actually just empty space left for Elon's ego. If you don't define a **border-box**, the browser automatically expands the element to make room for his Tesla stock portfolio.

"""
    
    return system_instruction + "\n\n" + conversation_history + "Assistant: "
def inject_fact_into_response(response_text: str, fact: Dict[str, str]) -> str:
    """
    Optionally inject a fact reference into a response
    (Alternative approach - not currently used)
    
    Args:
        response_text: The LLM's response
        fact: The fact to potentially reference
        
    Returns:
        Modified response text
    """
    # This could be used to explicitly mention facts in responses
    # Currently not used, but available for experimentation
    return response_text
