import ollama
import requests
import json
import random

# ---------------------------------------------------------
# 1. DEFINE THE TOOL
# ---------------------------------------------------------
VALID_CODES = ["AU", "BR", "CA", "CH", "DE", "DK", "ES", "GB", "IN", "US"]

def fetch_user_by_country(country_code):
    """
    Fetches a random user from a specific country code.
    If 'RANDOM' is passed, it picks one from the list.
    """
    code = country_code.strip().upper()

    # --- FIX: Handle Randomness in Python, not LLM ---
    if code == "RANDOM":
        code = random.choice(VALID_CODES)
        print(f"[Agent] 🎲 'ANY' detected. Rolling dice... Selected: {code}")
    
    # Validate code
    if code not in VALID_CODES:
        return {"error": f"Invalid code '{code}'. Valid codes are: {VALID_CODES}"}

    # Construct URL and Fetch
    url = f"https://open-api-ts.vercel.app/v0.1/user/{code}"
    print(f"[System] 🌐 Fetching data for country: {code}...")
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # We inject the used code into the response so we know what we got
            data = response.json()
            if "data" in data and "Address" in data["data"]:
                data["data"]["Address"]["CountryCode"] = code 
            return data
        else:
            return {"error": f"API returned status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# Tool Definition
tools_schema = [
    {
        "name": "fetch_user_by_country",
        "description": "Fetches a user profile. Use code 'RANDOM' if user asks for random/any.",
        "parameters": {
            "type": "object",
            "properties": {
                "country_code": {
                    "type": "string",
                    "description": "2-letter code (US, IN, etc) OR 'RANDOM'"
                }
            },
            "required": ["country_code"]
        }
    }
]

# ---------------------------------------------------------
# 2. AGENT LOGIC
# ---------------------------------------------------------
def run_agent(user_query):
    print(f"🤖 User asked: '{user_query}'")

    system_instruction = f"""
    You are a smart API Assistant. 
    You have access to a tool named 'fetch_user_by_country'.
    
    Your goal is to map the user's country request to a code:
    {json.dumps(VALID_CODES)}
    
    RULES:
    1. If user says "India" -> "IN", "USA" -> "US", etc.
    2. If user says "ANY", "Random", "Surprise me", or "Whatever" -> use code "RANDOM".
    3. If user query is unrelated, reply with a text message.
    
    Output strictly JSON:
    {{
        "tool": "fetch_user_by_country",
        "arguments": {{ "country_code": "CODE_OR_RANDOM" }}
    }}
    """

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_query}
    ]

    try:
        response = ollama.chat(model='gemma3', messages=messages, format='json')
        content = response['message']['content']
        decision = json.loads(content)

        print("\n=================== LLM DECISION ===================")
        print(json.dumps(decision, indent=2))
        print("====================================================\n")
        
        if decision.get("tool") == "fetch_user_by_country":
            code = decision["arguments"].get("country_code")
            return fetch_user_by_country(code)
        elif "message" in decision:
            return decision
        else:
            return {"message": content}

    except Exception as e:
        return {"error": f"Agent error: {str(e)}"}

# ---------------------------------------------------------
# 3. TEST RUN
# ---------------------------------------------------------
if __name__ == "__main__":
    result = run_agent("Supprise me")
    
    if "data" in result:
        print(f"📝 Name: {result['data'].get('FirstName')}")
        print(f"🌍 Country: {result['data']['Address'].get('CountryCode')}")
    else:
        print("📝 Result:", result)