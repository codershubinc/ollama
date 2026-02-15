"""
Main Flask application
Modular chat application with Ollama integration and SQLite storage
"""

from flask import Flask, render_template
from flask_cors import CORS
import os
from database import init_db, create_chat
from routes import api

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Register blueprints
app.register_blueprint(api)

# =============================================================================
# MAIN ROUTES
# =============================================================================

@app.route('/')
def home():
    """Render main chat interface"""
    return render_template('chat.html')

# =============================================================================
# STARTUP
# =============================================================================

def initialize_app():
    """Initialize database and create default chat if needed"""
    if not os.path.exists('chats.db'):
        print("📦 Initializing database...")
        init_db()
        print("✅ Database created")
        
        # Create welcome chat
        chat = create_chat('Welcome Chat')
        print(f"💬 Created welcome chat (ID: {chat['id']})")

if __name__ == '__main__':
    initialize_app()
    print("🚀 Starting Ollama Chat Application")
    print("📍 Running on http://localhost:5000")
    app.run(debug=True, port=5000, host="0.0.0.0")