# Integration & Usage

Quick steps to run the integrated dark-themed chat and the extension-info page:

1. Ensure you have Python 3.8+ and the requirements installed:

   pip install -r requirements.txt

2. Ensure your local model server (the one listening on port `11434`) is running and accessible. The app proxies `/api/generate` to `http://localhost:11434/api/generate`.

3. Start the Flask app:

   python app.py

4. Open the app in your browser:

   - Chat UI: http://localhost:5000/
   - Extension info: http://localhost:5000/maket

Examples: Using the Ollama helper endpoint

- Short form (convenience):

  curl -s -X POST http://localhost:5000/api/ollama_chat -H 'Content-Type: application/json' -d '{"model":"gemma3","prompt":"Why is the sky blue?"}' | jq

- Full messages form:

  curl -s -X POST http://localhost:5000/api/ollama_chat -H 'Content-Type: application/json' -d '{"model":"gemma3","messages":[{"role":"user","content":"Explain dependency injection"}]}' | jq

Notes:

- `fetch_stream.py` is a small CLI helper to test streaming responses directly from the model server.
- The frontend uses `/api/generate` so the browser doesn't need to talk directly to port 11434 (avoids CORS issues).

Non-streaming aggregation

If you prefer a single, clear JSON or plain-text response instead of streamed NDJSON, use the aggregate endpoint which collects fragments and returns a consolidated result:

- Aggregate (JSON mode):

  curl -s -X POST http://localhost:5000/api/generate/aggregate -H 'Content-Type: application/json' -d '{"model":"gemma3","prompt":"Explain dependency injection","meta":{"response_mode":"json"}}' | jq

- Aggregate (text mode):

  curl -s -X POST http://localhost:5000/api/generate/aggregate -H 'Content-Type: application/json' -d '{"model":"gemma3","prompt":"Summarize Go channels","stream":false}'

This endpoint attempts to parse streamed NDJSON fragments and return a single clean JSON object or combined text, avoiding raw bytes in responses.