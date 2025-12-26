import requests
import base64

# Simple prompt to test speed and memory
payload = {
    "prompt": "a green apple",
    "steps": 15
}

print("🎨 Sending request to Stable Diffusion...")
try:
    response = requests.post('http://127.0.0.1:7860/sdapi/v1/txt2img', json=payload)
    
    if response.status_code == 200:
        r = response.json()
        image_data = base64.b64decode(r['images'][0])
        with open("test_apple.png", "wb") as f:
            f.write(image_data)
        print("✅ Success! Image saved as 'test_apple.png'")
    else:
        print(f"❌ Server Error: {response.status_code}")
        
except Exception as e:
    print(f"❌ Connection Error: {e}")
    print("   (Make sure WebUI Forge is running with --api)")