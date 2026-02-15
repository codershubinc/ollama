# Ollama Chat Application

A modern, modular chat application with local Ollama integration, SQLite storage, and a beautiful dark-themed UI.

## Features

- 🤖 **Local AI** - Runs completely locally with Ollama
- 💾 **Persistent Storage** - SQLite database for chat history
- 💬 **Multiple Chats** - Create and manage multiple conversations
- 🎨 **Modern UI** - Dark theme with Tailwind CSS
- 📦 **Modular Architecture** - Clean, maintainable code structure
- ⚡ **Real-time Streaming** - See responses as they're generated
- 🤪 **Crazy Mode** - Blend random facts into AI responses for creative, unexpected answers!

## Architecture

The application follows a modular design:

```
simple_chat/
├── app.py              # Main Flask application
├── database.py         # Database operations & queries
├── ollama_service.py   # Ollama API communication
├── facts_service.py    # Random facts API for crazy mode
├── routes.py           # API endpoints (Blueprint)
├── templates/
│   └── chat.html       # Modern UI interface
├── chats.db            # SQLite database (auto-created)
└── requirements.txt    # Python dependencies
```

### Modules

- **app.py** - Main application entry point, registers blueprints
- **database.py** - All database operations (CRUD for chats & messages)
- **ollama_service.py** - Handles streaming communication with Ollama API
- **facts_service.py** - Fetches random facts and creates creative prompts
- **routes.py** - Flask Blueprint with all API endpoints
- **chat.html** - Single-page application with modern UI

## Installation

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Make sure Ollama is running:**

   ```bash
   ollama serve
   ```

3. **Start the application:**

   ```bash
   python app.py
   ```

4. **Open in browser:**
   ```
   http://localhost:5000
   ```

## Usage

### Create a New Chat

- Click the "New Chat" button in the sidebar
- Start typing your message and press Enter

### Switch Between Chats

- Click on any chat in the sidebar to view its history
- The most recent chat is shown at the top

### Delete a Chat

- Click the trash icon that appears when hovering over a chat
- Or use the delete button in the header when viewing a chat

### Change Model

- Use the model dropdown in the header to switch between:
  - Gemma 3
  - DeepSeek R1
  - Llama 3
  - Mistral
  - (All installed models dynamically loaded)

### Crazy Mode 🤪

- Toggle the "Crazy" switch in the header to enable/disable
- When enabled, each response is influenced by a random fact from the internet
- The AI's responses become more creative, unexpected, and entertaining
- Facts are shown at the bottom of each message to see what influenced the response
- Perfect for brainstorming, creative writing, or just having fun!

## API Endpoints

### Chats

- `GET /api/chats` - Get all chats
- `POST /api/chats` - Create new chat
- `PUT /api/chats/<id>` - Update chat title
- `DELETE /api/chats/<id>` - Delete chat

### Messages

- `GET /api/chats/<id>/messages` - Get chat messages
- `POST /api/chats/<id>/messages` - Send message (streaming response)

## Database Schema

### chats table

```sql
id           INTEGER PRIMARY KEY
title        TEXT
created_at   TIMESTAMP
updated_at   TIMESTAMP
```

### messages table

```sql
id           INTEGER PRIMARY KEY
chat_id      INTEGER (FK)
role         TEXT ('user' | 'assistant')
content      TEXT
created_at   TIMESTAMP
```

## Requirements

- Python 3.7+
- Flask
- Flask-CORS
- Requests
- Ollama (running locally on port 11434)

## Development

The app runs in debug mode by default. Changes to Python files will auto-reload.

To modify the UI, edit `templates/chat.html`. Tailwind CSS is loaded from CDN.

## License

MIT
