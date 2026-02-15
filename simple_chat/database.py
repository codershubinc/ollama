"""
Database module for chat application
Handles all database operations and queries
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

DATABASE = 'chats.db'

def get_db():
    """Get database connection with row factory"""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Initialize database tables"""
    db = get_db()
    
    # Create chats table
    db.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create messages table
    db.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
        )
    ''')
    
    db.commit()
    db.close()

# =============================================================================
# CHAT OPERATIONS
# =============================================================================

def get_all_chats() -> List[Dict]:
    """Get all chats ordered by most recent"""
    db = get_db()
    chats = db.execute(
        'SELECT * FROM chats ORDER BY updated_at DESC'
    ).fetchall()
    db.close()
    return [dict(chat) for chat in chats]

def create_chat(title: str = 'New Chat') -> Dict:
    """Create a new chat"""
    db = get_db()
    cursor = db.execute(
        'INSERT INTO chats (title) VALUES (?)',
        (title,)
    )
    chat_id = cursor.lastrowid
    db.commit()
    
    chat = db.execute('SELECT * FROM chats WHERE id = ?', (chat_id,)).fetchone()
    db.close()
    
    return dict(chat) if chat else None

def delete_chat(chat_id: int) -> bool:
    """Delete a chat and all its messages"""
    db = get_db()
    db.execute('DELETE FROM chats WHERE id = ?', (chat_id,))
    db.commit()
    db.close()
    return True

def update_chat_title(chat_id: int, title: str) -> bool:
    """Update chat title"""
    db = get_db()
    db.execute(
        'UPDATE chats SET title = ?, updated_at = ? WHERE id = ?',
        (title, datetime.now(), chat_id)
    )
    db.commit()
    db.close()
    return True

def update_chat_timestamp(chat_id: int) -> bool:
    """Update chat's last modified timestamp"""
    db = get_db()
    db.execute(
        'UPDATE chats SET updated_at = ? WHERE id = ?',
        (datetime.now(), chat_id)
    )
    db.commit()
    db.close()
    return True

# =============================================================================
# MESSAGE OPERATIONS
# =============================================================================

def get_chat_messages(chat_id: int) -> List[Dict]:
    """Get all messages for a specific chat"""
    db = get_db()
    messages = db.execute(
        'SELECT * FROM messages WHERE chat_id = ? ORDER BY created_at ASC',
        (chat_id,)
    ).fetchall()
    db.close()
    return [dict(msg) for msg in messages]

def create_message(chat_id: int, role: str, content: str) -> Dict:
    """Create a new message"""
    db = get_db()
    cursor = db.execute(
        'INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)',
        (chat_id, role, content)
    )
    message_id = cursor.lastrowid
    db.commit()
    
    message = db.execute('SELECT * FROM messages WHERE id = ?', (message_id,)).fetchone()
    db.close()
    
    return dict(message) if message else None

def get_chat_history(chat_id: int) -> str:
    """Build conversation history as formatted string"""
    messages = get_chat_messages(chat_id)
    
    history = ""
    for msg in messages:
        role = "User" if msg['role'] == 'user' else "Assistant"
        history += f"{role}: {msg['content']}\n"
    
    return history
