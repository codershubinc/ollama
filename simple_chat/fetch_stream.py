from ollama import chat
from ollama import ChatResponse

response: ChatResponse = chat(model='gemma3', messages=[
  {
    'role':""" system , # Output Format
Return ONLY   JSON.""",
    'content': 'hi!!',
  },
])
# print(response['message']['content'])
# or access fields directly from the response object
print(response.message.content)

 