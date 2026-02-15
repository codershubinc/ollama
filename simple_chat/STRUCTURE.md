# Project Structure

This is a modular Ollama Chat application with clean separation of concerns.

## Directory Structure

```
simple_chat/
├── app.py                  # Main Flask application & initialization
├── database.py             # Database operations (SQLite)
├── ollama_service.py       # Ollama API service layer
├── routes.py               # API routes (Flask Blueprint)
├── requirements.txt        # Python dependencies
├── chats.db               # SQLite database (auto-created)
├── README.md              # Full documentation
│
├── templates/
│   └── chat.html          # Modern dark-themed UI
│
└── static/
    └── css/               # (optional custom CSS)
```

## Module Descriptions

### `app.py` (Main Application)
- Initializes Flask app
- Registers blueprints
- Database initialization
- Application entry point

**Key Functions:**
- `initialize_app()` - Sets up database on first run

---

### `database.py` (Data Layer)
- All SQLite operations
- Type-safe functions with type hints
- Two tables: `chats` and `messages`

**Key Functions:**
- `get_all_chats()` - Fetch all chats
- `create_chat(title)` - Create new chat
- `delete_chat(chat_id)` - Delete chat & messages
- `get_chat_messages(chat_id)` - Get messages
- `create_message(chat_id, role, content)` - Save message
- `get_chat_history(chat_id)` - Build conversation string

---

### `ollama_service.py` (External API Layer)
- Communication with Ollama API
- Streaming response handling
- Model discovery

**Key Functions:**
- `stream_ollama_response(prompt, model)` - Stream AI responses
- `get_available_models()` - Fetch installed Ollama models
- `get_ollama_response(prompt, model)` - Non-streaming response

---

### `routes.py` (API Layer)
- Flask Blueprint with REST endpoints
- Request/response handling
- Coordinates between database and Ollama service

**Endpoints:**
- `GET /api/models` - List available models
- `GET /api/chats` - List all chats
- `POST /api/chats` - Create new chat
- `DELETE /api/chats/<id>` - Delete chat
- `PUT /api/chats/<id>` - Update chat title
- `GET /api/chats/<id>/messages` - Get messages
- `POST /api/chats/<id>/messages` - Send message (streaming)

---

### `chat.html` (Frontend)
- Modern dark theme with Tailwind CSS
- Real-time message streaming
- Responsive sidebar
- Dynamic model loading

**Features:**
- Auto-loads available Ollama models
- Creates/manages multiple chats
- Formats messages with proper styling
- Smooth scrolling & animations

---

## Data Flow

```
User Input (chat.html)
    ↓
API Route (routes.py)
    ↓
Database Save (database.py) ← User message saved
    ↓
Ollama Service (ollama_service.py) ← Generate AI response
    ↓
Stream Response back to Frontend
    ↓
Database Save (database.py) ← Assistant message saved
```

## Benefits of Modular Structure

1. **Separation of Concerns** - Each module has a single responsibility
2. **Testability** - Easy to test individual modules
3. **Maintainability** - Changes are localized to specific files
4. **Reusability** - Modules can be imported elsewhere
5. **Scalability** - Easy to add new features
6. **Readability** - Clear organization makes code easy to understand

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Make sure Ollama is running
ollama serve

# Pull a model if you don't have one
ollama pull llama3

# Start the app
python app.py
```

Visit http://localhost:5000 to use the chat interface!
