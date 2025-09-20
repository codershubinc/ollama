import requests
import json

print("Enter your prompt: \n")
input_prompt =  input()

url = "http://localhost:11434/api/generate"
headers = {
    "Content-Type": "application/json"
}
data = {
    "model": "deepseek-r1:14b",
    "prompt": input_prompt,
    "stream": True
}

response = requests.post(url, headers=headers, json=data, stream=True)

if response.status_code == 200:
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line.decode('utf-8'))
            if 'response' in chunk:
                print(chunk['response'], end='', flush=True)
            if chunk.get('done', False):
                break
else:
    print(f"Error: {response.status_code} - {response.text}")