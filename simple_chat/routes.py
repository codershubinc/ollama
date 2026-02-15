"""
Routes module for chat application
Defines all API endpoints
"""

from flask import Blueprint, jsonify, request, Response
import json
from database import (
    get_all_chats, create_chat, delete_chat, update_chat_title,
    get_chat_messages, create_message, update_chat_timestamp, get_chat_history
)
from ollama_service import stream_ollama_response, get_available_models
from facts_service import get_random_fact, create_crazy_prompt

api = Blueprint('api', __name__, url_prefix='/api')

# =============================================================================
# MODEL ROUTES
# =============================================================================

@api.route('/models', methods=['GET'])
def get_models():
    """Get available Ollama models"""
    models = get_available_models()
    return jsonify(models)

# =============================================================================
# CHAT ROUTES
# =============================================================================

@api.route('/chats', methods=['GET'])
def get_chats():
    """Get all chats"""
    chats = get_all_chats()
    return jsonify(chats)

@api.route('/chats', methods=['POST'])
def create_new_chat():
    """Create a new chat"""
    data = request.get_json() or {}
    title = data.get('title', 'New Chat')
    
    chat = create_chat(title)
    return jsonify(chat), 201

@api.route('/chats/<int:chat_id>', methods=['DELETE'])
def remove_chat(chat_id):
    """Delete a chat"""
    success = delete_chat(chat_id)
    return jsonify({'success': success})

@api.route('/chats/<int:chat_id>', methods=['PUT'])
def update_chat(chat_id):
    """Update chat title"""
    data = request.get_json() or {}
    title = data.get('title')
    
    if not title:
        return jsonify({'error': 'Title required'}), 400
    
    success = update_chat_title(chat_id, title)
    return jsonify({'success': success})

# =============================================================================
# MESSAGE ROUTES
# =============================================================================

@api.route('/chats/<int:chat_id>/messages', methods=['GET'])
def get_messages(chat_id):
    """Get all messages for a chat"""
    messages = get_chat_messages(chat_id)
    return jsonify(messages)

@api.route('/chats/<int:chat_id>/messages', methods=['POST'])
def send_message(chat_id):
    """Send message and stream Ollama response"""
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    model = data.get('model', '')
    crazy_mode = data.get('crazy_mode', True)  # Default to crazy mode on
    
    if not user_message:
        return jsonify({'error': 'Message required'}), 400
    
    # If no model specified, try to get first available model
    if not model or model == '':
        models = get_available_models()
        if models and len(models) > 0:
            model = models[0]['name']
        else:
            return jsonify({'error': 'No Ollama models available. Please install a model first.'}), 400
    
    # Save user message
    create_message(chat_id, 'user', user_message)
    update_chat_timestamp(chat_id)
    
    # Get conversation history
    history = get_chat_history(chat_id)
    
    # Get random fact and create crazy prompt (only if crazy mode is enabled)
    fact = None
    if crazy_mode:
        fact = get_random_fact()
        prompt = create_crazy_prompt(history, fact)
    else:
        prompt = history + "Assistant: "
    
    # Stream response
    def generate():
        full_response = ""
        
        for chunk in stream_ollama_response(prompt, model):
            if 'error' in chunk:
                yield json.dumps(chunk) + '\n'
                return
            
            if 'response' in chunk:
                full_response += chunk['response']
            
            yield json.dumps(chunk) + '\n'
            
            # Save complete response when done
            if chunk.get('done'):
                # Add fact metadata to final chunk
                if fact:
                    chunk['fact_used'] = fact
                yield json.dumps(chunk) + '\n'
                create_message(chat_id, 'assistant', full_response)
    
    return Response(generate(), content_type='application/x-ndjson')
