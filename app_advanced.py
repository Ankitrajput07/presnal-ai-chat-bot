from flask import Flask, request, jsonify, render_template_string, Response
from flask_cors import CORS
import requests
import json
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    MODEL_NAME = os.getenv('MODEL_NAME', 'gemma3:1b')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# HTML Template with enhanced features
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Personal AI Chat Agent</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            color: #e2e8f0;
            height: 100vh;
            overflow: hidden;
        }

        .chat-container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            max-width: 900px;
            margin: 0 auto;
            background: rgba(30, 41, 59, 0.95);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(100, 116, 139, 0.2);
            box-shadow: 0 0 50px rgba(0, 0, 0, 0.5);
        }

        .chat-header {
            background: linear-gradient(90deg, #4f46e5, #7c3aed);
            padding: 1rem;
            border-bottom: 1px solid rgba(100, 116, 139, 0.3);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .chat-header h1 {
            font-size: 1.5rem;
            font-weight: 600;
        }

        .status {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.875rem;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10b981;
            animation: pulse 2s infinite;
        }

        .status-dot.disconnected {
            background: #ef4444;
        }

        .model-badge {
            background: rgba(255, 255, 255, 0.2);
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.75rem;
            font-weight: 500;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            scroll-behavior: smooth;
        }

        .message {
            margin-bottom: 1rem;
            display: flex;
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message.user {
            justify-content: flex-end;
        }

        .message.ai {
            justify-content: flex-start;
        }

        .message-content {
            max-width: 75%;
            padding: 0.875rem 1.125rem;
            border-radius: 1rem;
            word-wrap: break-word;
            line-height: 1.6;
            position: relative;
        }

        .message.user .message-content {
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: white;
            border-bottom-right-radius: 0.25rem;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        }

        .message.ai .message-content {
            background: rgba(55, 65, 81, 0.9);
            border: 1px solid rgba(100, 116, 139, 0.2);
            border-bottom-left-radius: 0.25rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }

        .message-time {
            font-size: 0.75rem;
            opacity: 0.7;
            margin-top: 0.25rem;
        }

        .typing-indicator {
            display: none;
            justify-content: flex-start;
            margin-bottom: 1rem;
        }

        .typing-indicator.active {
            display: flex;
        }

        .typing-dots {
            background: rgba(55, 65, 81, 0.9);
            padding: 0.875rem 1.125rem;
            border-radius: 1rem;
            border-bottom-left-radius: 0.25rem;
            border: 1px solid rgba(100, 116, 139, 0.2);
        }

        .typing-animation {
            display: flex;
            gap: 0.25rem;
            align-items: center;
        }

        .typing-animation::before {
            content: "AI is typing";
            font-size: 0.75rem;
            margin-right: 0.5rem;
            opacity: 0.7;
        }

        .typing-animation span {
            width: 6px;
            height: 6px;
            background: #94a3b8;
            border-radius: 50%;
            animation: typing 1.5s infinite;
        }

        .typing-animation span:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-animation span:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes typing {
            0%, 60%, 100% {
                transform: translateY(0);
                opacity: 0.5;
            }
            30% {
                transform: translateY(-10px);
                opacity: 1;
            }
        }

        .chat-input {
            padding: 1rem;
            border-top: 1px solid rgba(100, 116, 139, 0.3);
            background: rgba(30, 41, 59, 0.5);
            backdrop-filter: blur(10px);
        }

        .input-container {
            display: flex;
            gap: 0.75rem;
            align-items: end;
        }

        .input-field {
            flex: 1;
            min-height: 48px;
            max-height: 120px;
            padding: 0.875rem;
            border: 1px solid rgba(100, 116, 139, 0.3);
            border-radius: 0.75rem;
            background: rgba(30, 41, 59, 0.9);
            color: #e2e8f0;
            resize: none;
            font-family: inherit;
            font-size: 0.9rem;
            line-height: 1.5;
            transition: all 0.2s ease;
        }

        .input-field:focus {
            outline: none;
            border-color: #4f46e5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
            background: rgba(30, 41, 59, 1);
        }

        .input-field::placeholder {
            color: #64748b;
        }

        .send-button {
            min-width: 48px;
            height: 48px;
            border: none;
            border-radius: 0.75rem;
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3);
        }

        .send-button:hover:not(:disabled) {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4);
        }

        .send-button:active:not(:disabled) {
            transform: translateY(0);
        }

        .send-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .controls {
            display: flex;
            gap: 0.5rem;
        }

        .control-button {
            width: 36px;
            height: 36px;
            border: none;
            border-radius: 0.5rem;
            background: rgba(100, 116, 139, 0.2);
            color: #94a3b8;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }

        .control-button:hover {
            background: rgba(100, 116, 139, 0.3);
            color: #e2e8f0;
        }

        .error-toast {
            position: fixed;
            top: 1rem;
            right: 1rem;
            background: #ef4444;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 0.75rem;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 1000;
            max-width: 400px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .error-toast.show {
            transform: translateX(0);
        }

        .welcome-message {
            text-align: center;
            padding: 3rem 2rem;
            opacity: 0.8;
        }

        .welcome-message h2 {
            font-size: 1.5rem;
            margin-bottom: 0.75rem;
            color: #4f46e5;
            font-weight: 600;
        }

        .welcome-message p {
            color: #94a3b8;
            line-height: 1.6;
            font-size: 1rem;
        }

        .connection-status {
            margin-top: 1rem;
            padding: 0.75rem;
            border-radius: 0.5rem;
            font-size: 0.875rem;
        }

        .connection-status.connected {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #10b981;
        }

        .connection-status.disconnected {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #ef4444;
        }

        /* Scrollbar styling */
        .chat-messages::-webkit-scrollbar {
            width: 8px;
        }

        .chat-messages::-webkit-scrollbar-track {
            background: rgba(30, 41, 59, 0.5);
            border-radius: 4px;
        }

        .chat-messages::-webkit-scrollbar-thumb {
            background: rgba(100, 116, 139, 0.5);
            border-radius: 4px;
        }

        .chat-messages::-webkit-scrollbar-thumb:hover {
            background: rgba(100, 116, 139, 0.7);
        }

        /* Responsive design */
        @media (max-width: 768px) {
            .chat-container {
                height: 100vh;
                border: none;
                border-radius: 0;
                max-width: 100%;
            }

            .message-content {
                max-width: 85%;
            }

            .chat-header {
                padding: 0.75rem;
            }

            .chat-header h1 {
                font-size: 1.25rem;
            }

            .welcome-message {
                padding: 2rem 1rem;
            }

            .controls {
                display: none;
            }
        }

        /* Dark scrollbar for Firefox */
        .chat-messages {
            scrollbar-width: thin;
            scrollbar-color: rgba(100, 116, 139, 0.5) rgba(30, 41, 59, 0.5);
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <div class="header-left">
                <div>
                    <h1>🤖 Personal AI Chat Agent</h1>
                    <div class="status">
                        <span class="status-dot" id="statusDot"></span>
                        <span id="statusText">Checking connection...</span>
                    </div>
                </div>
            </div>
            <div class="model-badge" id="modelBadge">{{ model_name }}</div>
        </div>

        <div class="chat-messages" id="chatMessages">
            <div class="welcome-message">
                <h2>Welcome to your Personal AI Assistant!</h2>
                <p>Start a conversation by typing a message below. Your local Ollama model is ready to help you with any questions or tasks.</p>
                <div class="connection-status" id="connectionStatus">
                    <span id="connectionMessage">Checking Ollama connection...</span>
                </div>
            </div>
        </div>

        <div class="typing-indicator" id="typingIndicator">
            <div class="typing-dots">
                <div class="typing-animation">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>

        <div class="chat-input">
            <form class="input-container" id="messageForm">
                <textarea 
                    class="input-field" 
                    id="messageInput" 
                    placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
                    rows="1"
                    required
                ></textarea>
                <div class="controls">
                    <button type="button" class="control-button" id="clearButton" title="Clear chat">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M3 6h18M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
                        </svg>
                    </button>
                </div>
                <button class="send-button" type="submit" id="sendButton">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="m22 2-7 20-4-9-9-4z"/>
                        <path d="M22 2 11 13"/>
                    </svg>
                </button>
            </form>
        </div>
    </div>

    <div class="error-toast" id="errorToast">
        <strong>Connection Error</strong><br>
        <span id="errorMessage">Unable to connect to Ollama. Please make sure Ollama is running on localhost:11434</span>
    </div>

    <script>
        class ChatApp {
            constructor() {
                this.chatMessages = document.getElementById('chatMessages');
                this.messageInput = document.getElementById('messageInput');
                this.messageForm = document.getElementById('messageForm');
                this.sendButton = document.getElementById('sendButton');
                this.clearButton = document.getElementById('clearButton');
                this.typingIndicator = document.getElementById('typingIndicator');
                this.errorToast = document.getElementById('errorToast');
                this.statusDot = document.getElementById('statusDot');
                this.statusText = document.getElementById('statusText');
                this.connectionStatus = document.getElementById('connectionStatus');
                this.connectionMessage = document.getElementById('connectionMessage');

                this.isWaitingForResponse = false;
                this.messageHistory = [];

                this.init();
            }

            init() {
                this.setupEventListeners();
                this.adjustTextareaHeight();
                this.checkConnection();
                this.messageInput.focus();
            }

            setupEventListeners() {
                // Form submission
                this.messageForm.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.handleSendMessage();
                });

                // Input field events
                this.messageInput.addEventListener('input', () => {
                    this.adjustTextareaHeight();
                });

                this.messageInput.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        if (!this.isWaitingForResponse && this.messageInput.value.trim()) {
                            this.handleSendMessage();
                        }
                    }
                });

                // Clear chat button
                this.clearButton.addEventListener('click', () => {
                    this.clearChat();
                });

                // Auto-hide error toast
                this.errorToast.addEventListener('click', () => {
                    this.hideError();
                });
            }

            adjustTextareaHeight() {
                this.messageInput.style.height = 'auto';
                this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
            }

            async checkConnection() {
                try {
                    const response = await fetch('/api/health');
                    const data = await response.json();

                    if (data.ollama === 'connected') {
                        this.updateConnectionStatus(true);
                    } else {
                        this.updateConnectionStatus(false);
                    }
                } catch (error) {
                    this.updateConnectionStatus(false);
                }
            }

            updateConnectionStatus(connected) {
                if (connected) {
                    this.statusDot.classList.remove('disconnected');
                    this.statusText.textContent = 'Connected to Ollama';
                    this.connectionStatus.classList.remove('disconnected');
                    this.connectionStatus.classList.add('connected');
                    this.connectionMessage.textContent = '✅ Connected to Ollama - Ready to chat!';
                } else {
                    this.statusDot.classList.add('disconnected');
                    this.statusText.textContent = 'Disconnected';
                    this.connectionStatus.classList.remove('connected');
                    this.connectionStatus.classList.add('disconnected');
                    this.connectionMessage.textContent = '❌ Cannot connect to Ollama. Please ensure it is running.';
                }
            }

            async handleSendMessage() {
                const message = this.messageInput.value.trim();
                if (!message || this.isWaitingForResponse) return;

                // Add user message to chat
                this.addMessage(message, 'user');
                this.messageHistory.push({ role: 'user', content: message });

                // Clear input and reset height
                this.messageInput.value = '';
                this.adjustTextareaHeight();

                // Show typing indicator
                this.showTypingIndicator();

                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ 
                            message: message,
                            history: this.messageHistory.slice(-10) // Send last 10 messages for context
                        })
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }

                    const data = await response.json();

                    // Hide typing indicator
                    this.hideTypingIndicator();

                    // Add AI response to chat
                    this.addMessage(data.response, 'ai');
                    this.messageHistory.push({ role: 'assistant', content: data.response });

                } catch (error) {
                    console.error('Error:', error);
                    this.hideTypingIndicator();
                    this.showError('Failed to get response from AI. Please check your connection.');
                    this.addMessage('Sorry, I encountered an error while processing your message. Please make sure Ollama is running and try again.', 'ai');
                }
            }

            addMessage(content, type) {
                const messageElement = document.createElement('div');
                messageElement.className = `message ${type}`;

                const messageContent = document.createElement('div');
                messageContent.className = 'message-content';

                // Add message text
                const textElement = document.createElement('div');
                textElement.textContent = content;
                messageContent.appendChild(textElement);

                // Add timestamp
                const timeElement = document.createElement('div');
                timeElement.className = 'message-time';
                timeElement.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                messageContent.appendChild(timeElement);

                messageElement.appendChild(messageContent);

                // Remove welcome message if present
                const welcomeMessage = this.chatMessages.querySelector('.welcome-message');
                if (welcomeMessage) {
                    welcomeMessage.remove();
                }

                this.chatMessages.appendChild(messageElement);

                // Auto-scroll to bottom
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            }

            showTypingIndicator() {
                this.isWaitingForResponse = true;
                this.sendButton.disabled = true;
                this.typingIndicator.classList.add('active');
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            }

            hideTypingIndicator() {
                this.isWaitingForResponse = false;
                this.sendButton.disabled = false;
                this.typingIndicator.classList.remove('active');
                this.messageInput.focus();
            }

            showError(message) {
                document.getElementById('errorMessage').textContent = message || 'An unexpected error occurred.';
                this.errorToast.classList.add('show');
                setTimeout(() => {
                    this.hideError();
                }, 5000);
            }

            hideError() {
                this.errorToast.classList.remove('show');
            }

            clearChat() {
                const messages = this.chatMessages.querySelectorAll('.message');
                messages.forEach(message => message.remove());
                this.messageHistory = [];

                // Show welcome message again
                const welcomeMessage = document.createElement('div');
                welcomeMessage.className = 'welcome-message';
                welcomeMessage.innerHTML = `
                    <h2>Welcome to your Personal AI Assistant!</h2>
                    <p>Start a conversation by typing a message below. Your local Ollama model is ready to help you with any questions or tasks.</p>
                    <div class="connection-status connected" id="connectionStatus">
                        <span id="connectionMessage">✅ Connected to Ollama - Ready to chat!</span>
                    </div>
                `;
                this.chatMessages.appendChild(welcomeMessage);

                this.messageInput.focus();
            }
        }

        // Initialize the chat app when DOM is loaded
        document.addEventListener('DOMContentLoaded', () => {
            new ChatApp();
        });
    </script>
</body>
</html>
"""

def check_ollama_connection():
    """Check if Ollama server is running and accessible."""
    try:
        response = requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def get_ollama_response(message, history=None):
    """Get response from Ollama API with conversation context."""
    try:
        # Build conversation history
        messages = []
        if history:
            messages.extend(history)
        else:
            messages.append({
                "role": "user",
                "content": message
            })

        payload = {
            "model": Config.MODEL_NAME,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "max_tokens": 2000
            }
        }

        response = requests.post(
            f"{Config.OLLAMA_BASE_URL}/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            logger.error(f"Ollama API error: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return None
    except KeyError as e:
        logger.error(f"Unexpected response format: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return None

@app.route('/')
def index():
    """Serve the main chat interface."""
    return render_template_string(HTML_TEMPLATE, model_name=Config.MODEL_NAME)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and return AI responses."""
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        user_message = data['message'].strip()
        history = data.get('history', [])

        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        # Check Ollama connection
        if not check_ollama_connection():
            return jsonify({
                'error': 'Ollama server not accessible',
                'response': f'Sorry, I cannot connect to the Ollama server. Please make sure Ollama is running on {Config.OLLAMA_BASE_URL} and the {Config.MODEL_NAME} model is available.'
            }), 503

        # Get response from Ollama
        ai_response = get_ollama_response(user_message, history)

        if ai_response is None:
            return jsonify({
                'error': 'Failed to get AI response',
                'response': 'Sorry, I encountered an error while processing your message. Please try again.'
            }), 500

        return jsonify({
            'response': ai_response,
            'status': 'success',
            'model': Config.MODEL_NAME
        })

    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'response': 'Sorry, an unexpected error occurred. Please try again.'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify server and Ollama status."""
    ollama_status = check_ollama_connection()

    return jsonify({
        'server': 'running',
        'ollama': 'connected' if ollama_status else 'disconnected',
        'model': Config.MODEL_NAME,
        'ollama_url': Config.OLLAMA_BASE_URL,
        'timestamp': request.environ.get('HTTP_DATE', 'unknown')
    })

@app.route('/api/models', methods=['GET'])
def list_models():
    """List available Ollama models."""
    try:
        if not check_ollama_connection():
            return jsonify({'error': 'Ollama server not accessible'}), 503

        response = requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            return jsonify({'error': 'Failed to fetch models'}), 500

    except Exception as e:
        logger.error(f"Models endpoint error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Personal AI Chat Agent (Advanced Version)...")
    logger.info(f"Connecting to Ollama at: {Config.OLLAMA_BASE_URL}")
    logger.info(f"Using model: {Config.MODEL_NAME}")
    logger.info(f"Server will run on: {Config.FLASK_HOST}:{Config.FLASK_PORT}")

    # Check initial Ollama connection
    if check_ollama_connection():
        logger.info("✅ Ollama connection successful")
    else:
        logger.warning("⚠️  Ollama connection failed - please ensure Ollama is running")

    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.DEBUG)