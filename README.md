# presnal-ai-chat-bot
A self-hosted, personal AI chat agent powered by Flask and Ollama. This project provides a sleek, modern web UI to interact with your local language models privately. It features conversation history, a real-time connection status check, and a responsive design for a seamless chat experience on any device.


# 🤖 Personal AI Chat Agent

A sleek, self-hosted, and feature-rich chat interface for your local Ollama-powered language models. This project provides a simple yet powerful single-file Flask application that allows you to chat with any LLM running on your machine through a clean, modern web UI.



---

## ✨ Features

- **Sleek & Modern UI**: A beautiful, dark-themed, and responsive chat interface built with pure HTML, CSS, and JavaScript.
- **Ollama Integration**: Connects directly to your local Ollama instance.
- **Conversation History**: Maintains context by sending recent messages back to the model.
- **Real-time Status**: A connection indicator shows whether the frontend is successfully connected to the Ollama backend.
- **Streaming-Like Experience**: Includes a typing indicator to show when the AI is processing a response.
- **Dynamic UI Elements**: The message input box automatically resizes as you type.
- **Easy Configuration**: All settings (model name, host, port) are managed via a `.env` file.
- **Error Handling**: Displays user-friendly error messages if the connection to Ollama fails.
- **Single-File Application**: The entire application is contained within a single Python file for simplicity and portability.

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask, Flask-CORS
- **LLM Engine**: [Ollama](https://ollama.com/)
- **Frontend**: HTML5, CSS3, JavaScript (no frameworks)
- **Dependencies**: `requests`, `python-dotenv`

---

## 🚀 Getting Started

Follow these instructions to get the chat agent up and running on your local machine.

### Prerequisites

1.  **Python 3.8+**: Make sure you have Python installed.
    ```sh
    python --version
    ```
2.  **Ollama**: You must have Ollama installed and running. Follow the official instructions at [ollama.com](https://ollama.com/).
3.  **A Downloaded Model**: Pull a model to use with the chat agent. For example, to use `gemma3:1b`:
    ```sh
    ollama pull gemma3:1b
    ```

### Installation & Setup

1.  **Clone the Repository**:
    ```sh
    git clone [https://github.com/Ankitrajput07/personal-ai-chat-agent.git](https://github.com/Ankitrajput07/personal-ai-chat-agent.git)
    cd personal-ai-chat-agent
    ```

2.  **Create a Virtual Environment**:
    ```sh
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**: Create a `requirements.txt` file with the following content:
    ```txt
    Flask
    Flask-Cors
    requests
    python-dotenv
    ```
    Then, install the packages:
    ```sh
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**: Create a file named `.env` in the root directory and add the following configuration. Adjust the values if your setup is different.
    ```env
    # .env
    OLLAMA_BASE_URL=http://localhost:11434
    MODEL_NAME=gemma3:1b
    FLASK_PORT=5000
    FLASK_HOST=0.0.0.0
    DEBUG=True
    ```

### Running the Application

1.  **Start Ollama**: Make sure your local Ollama server is running.

2.  **Run the Flask App**:
    ```sh
    python app.py
    ```

3.  **Open the Chat Interface**: Open your web browser and navigate to:
    [http://localhost:5000](http://localhost:5000)

You should now see the chat interface, ready to accept your messages!

---

## ⚙️ Configuration

You can customize the application's behavior by modifying the `.env` file:

- `OLLAMA_BASE_URL`: The URL of your Ollama server.
- `MODEL_NAME`: The name of the Ollama model you want to chat with (e.g., `llama3`, `mistral`, `gemma3:1b`).
- `FLASK_PORT`: The port on which the Flask web server will run.
- `FLASK_HOST`: The host address for the Flask server. `0.0.0.0` makes it accessible on your local network.
- `DEBUG`: Set to `True` for development mode (provides detailed error logs) or `False` for production.

---

## 📝 API Endpoints

The Flask application exposes a few API endpoints:

- **`GET /`**: Serves the main HTML chat page.
- **`POST /api/chat`**: The main chat endpoint. It receives the user's message and history and returns the AI's response.
- **`GET /api/health`**: A health check endpoint that verifies the status of the Flask server and its connection to Ollama.
- **`GET /api/models`**: Lists all models available in your local Ollama instance.

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
