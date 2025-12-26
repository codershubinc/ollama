from flask import Flask, jsonify, request, render_template, Response, stream_with_context, send_file
from flask_cors import CORS
import requests
import json
from bs4 import BeautifulSoup
import base64
import random
from io import BytesIO

# Optional Ollama Python client
try:
    import ollama
except ImportError:
    ollama = None

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# =============================================================================
# 🔧 HELPER FUNCTIONS (Tools)
# =============================================================================
VALID_CODES = ["AU", "BR", "CA", "CH", "DE", "DK", "ES", "GB", "IN", "US"]

def fetch_user_by_country_logic(country_code):
    """
    Helper function to fetch user data. 
    Handles 'RANDOM' logic internally.
    """
    code = country_code.strip().upper()
    if code == "RANDOM":
        code = random.choice(VALID_CODES)
    
    if code not in VALID_CODES:
        return {"error": f"Invalid code '{code}'. Valid codes: {VALID_CODES}"}

    try:
        url = f"https://open-api-ts.vercel.app/v0.1/user/{code}"
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            # Inject the used country code for clarity
            if "data" in data and "Address" in data["data"]:
                 data["data"]["Address"]["CountryCode"] = code
            return data
        else:
            return {"error": f"API Error: {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# =============================================================================
# 🌐 ROUTES
# =============================================================================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape')
def scrape():
    url = 'https://marketplace.visualstudio.com/items?itemName=codershubinc.music'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Robust extraction
        def get_text(cls):
            el = soup.find(class_=cls)
            return el.get_text(strip=True) if el else 'Not found'

        return jsonify({
            'title': get_text('ux-item-name') or soup.find('span', class_='ux-item-name').get_text(strip=True),
            'publisher': get_text('ux-item-publisher-link  '),
            'description': get_text('body-M'),
            'installs': get_text('installs-text')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Text Generation (Streaming Proxy) ---
@app.route('/api/generate', methods=['POST'])
def proxy_generate():
    payload = request.get_json() or {}
    try:
        upstream = requests.post(
            'http://localhost:11434/api/generate', 
            json=payload, 
            stream=True, 
            timeout=(5, None)
        )
        if upstream.status_code != 200:
            return jsonify({'error': upstream.text}), upstream.status_code

        def generate():
            json_mode = payload.get('meta', {}).get('response_mode') == 'json'
            buf = "" if json_mode else None
            for chunk in upstream.iter_lines():
                if not chunk:
                    continue
                line = chunk + b"\n"

                if json_mode:
                    # Decode chunk (preserve whitespace/newlines for buffering)
                    s = chunk.decode('utf-8', errors='replace')
                    s_stripped = s.strip()

                    # First, try parsing the single chunk (covers NDJSON or full JSON in one chunk)
                    try:
                        parsed = json.loads(s_stripped)
                        yield (json.dumps(parsed) + "\n").encode('utf-8')
                        continue
                    except Exception:
                        pass

                    # Otherwise, accumulate into buffer and attempt to parse the accumulated content
                    buf += s
                    try:
                        parsed = json.loads(buf)
                        yield (json.dumps(parsed) + "\n").encode('utf-8')
                        buf = ""
                    except Exception:
                        # buffer is incomplete; wait for more fragments
                        continue
                else:
                    yield line

            # End of stream: if in json mode and buffer remains, try to recover/emit
            if json_mode and buf:
                try:
                    parsed = json.loads(buf)
                    yield (json.dumps(parsed) + "\n").encode('utf-8')
                except Exception:
                    # If still invalid, wrap remainder as a single response field (mark done)
                    wrapped = json.dumps({'response': buf, 'done': True}) + "\n"
                    yield wrapped.encode('utf-8')

        return Response(stream_with_context(generate()), content_type='application/x-ndjson')

    except Exception as e:
        return jsonify({'error': f"Ollama connection failed: {str(e)}"}), 500

# --- User Data Endpoint ---
@app.route("/api/user/<country_code>")
def get_user(country_code):
    """
    API to get a user. Example: /api/user/US or /api/user/RANDOM
    """
    return jsonify(fetch_user_by_country_logic(country_code))

# --- Image Generation Endpoint ---
@app.route('/api/generate-image', methods=['GET'])
def generate_image():
    """
    Generates an HD image using 'Hires Fix' to save VRAM.
    Usage: /api/generate-image?prompt=cyberpunk city&hd=true
    """
    prompt = request.args.get('prompt', 'a futuristic robot, 8k, highly detailed')
    is_hd = request.args.get('hd', 'false').lower() == 'true'
    
    # Base settings (Low VRAM friendly)
    payload = {
        "prompt": f"{prompt}, masterpiece, best quality, 8k, ultra detailed, highres",
        "negative_prompt": "blurry, low quality, ugly, deformed, pixelated, sketch",
        "steps": 20,
        "width": 512,
        "height": 512,
        "cfg_scale": 7,
        "sampler_name": "Euler a"
    }

    # If HD is requested, enable "Hires Fix" (Upscaling)
    if is_hd:
        print("🚀 HD Mode Enabled (Upscaling 2x)...")
        payload.update({
            "enable_hr": True,          # Enable High-Res Fix
            "hr_scale": 2,              # Upscale by 2x (512x512 -> 1024x1024)
            "hr_upscaler": "Latent",    # Fast upscaler
            "denoising_strength": 0.7   # How much to change the image during upscale
        })

    try:
        # Call local WebUI Forge
        resp = requests.post('http://127.0.0.1:7860/sdapi/v1/txt2img', json=payload)
        
        if resp.status_code != 200:
            return jsonify({'error': 'Stable Diffusion API Error', 'details': resp.text}), 500

        r = resp.json()
        if 'images' in r:
            image_data = base64.b64decode(r['images'][0])
            return send_file(BytesIO(image_data), mimetype='image/png')
        else:
            return jsonify({'error': 'No image returned'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Agent / JSON Chat Endpoint ---
@app.route('/api/chat/json', methods=['POST'])
def chat_json():
    """
    Smart endpoint that can output JSON, User Data, or (conceptually) Image URLs.
    """
    if ollama is None:
        return jsonify({'error': 'Ollama library missing'}), 500

    data = request.get_json() or {}
    user_msg = data.get('message') or data.get('prompt')
    model = data.get('model', 'gemma3')

    if not user_msg:
        return jsonify({'error': 'No message provided'}), 400

    # Advanced System Prompt
    system_instruction = """
    You are a JSON-only API.
    1. If user asks for random user data/profiles, output keys matching a user profile.
    2. If user asks for a specific country (e.g. India), act as if you fetched that data.
    3. If user simply chats, return {"message": "..."}.
    4. STRICT JSON ONLY. No markdown.
    """

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_msg}
    ]

    try:
        # Non-streamed chat for safety
        resp = ollama.chat(model=model, messages=messages, format='json', stream=False)
        content = resp['message']['content']
        return jsonify(json.loads(content))
    except Exception as e:
        return jsonify({'error': str(e), 'raw': content if 'content' in locals() else ''}), 500

if __name__ == '__main__':
    # Listen on all interfaces (0.0.0.0) so you can access it from other devices/VMs
    app.run(debug=True, port=5000, host="0.0.0.0")