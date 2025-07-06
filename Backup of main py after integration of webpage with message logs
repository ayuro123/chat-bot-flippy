from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI
import openai
import os
import traceback

print("🔍 OpenAI version:", openai.__version__)

# ✅ Load API key from environment variable
openai_api_key = os.environ.get("OPENAI_API_KEY")
print("🔐 Loaded OPENAI_API_KEY from environment:", openai_api_key[:8] + "..." if openai_api_key else "❌ None FOUND")

# ✅ Create OpenAI client
client = OpenAI(api_key=openai_api_key)

# ✅ Flask app setup
app = Flask(__name__)

# ✅ Message history (optional)
messages = []

@app.route("/")
def home():
    """Web UI showing message history"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SMS Chatbot Monitor</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background-color: #ffffff; color: #333333; }
            .card { border: 1px solid #dee2e6; box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075); }
            .alert-info { background-color: #d1ecf1; border-color: #bee5eb; color: #0c5460; }
        </style>
    </head>
    <body>
        <div class="container mt-4">
            <h1 class="mb-4">📱 SMS Chatbot Monitor</h1>
            <div class="card">
                <div class="card-header bg-light">
                    <h5 class="mb-0">Recent Messages</h5>
                </div>
                <div class="card-body">
                    <div id="messages-container"></div>
                </div>
            </div>
            <div class="mt-3">
                <button class="btn btn-primary" onclick="loadMessages()">Refresh</button>
                <small class="text-muted ms-3">Auto-refreshing every 5 seconds</small>
            </div>
        </div>
        <script>
            function loadMessages() {
                fetch('/api/messages')
                    .then(res => res.json())
                    .then(data => {
                        const container = document.getElementById('messages-container');
                        container.innerHTML = '';
                        data.messages.forEach(msg => {
                            const div = document.createElement('div');
                            div.className = 'alert alert-info mb-2';
                            div.innerHTML = `<strong>📩 Incoming:</strong> ${msg.incoming}<br><strong>🤖 Reply:</strong> ${msg.reply}`;
                            container.appendChild(div);
                        });
                    });
            }
            loadMessages();
            setInterval(loadMessages, 5000);
        </script>
    </body>
    </html>
    """
    return html

@app.route("/sms", methods=["POST"])
def sms_reply():
    incoming_msg = request.form.get("Body")

    try:
        system_prompt = (
            "You are a highly intelligent and versatile AI assistant. "
            "You can explain advanced medical and scientific concepts, solve math problems, define words, "
            "tell jokes, answer trivia, describe locations, summarize news, provide recipes, and more. "
            "You are designed to respond over SMS, so your answers must be clear, concise, and readable on a basic phone screen. "
            "Avoid unnecessary formatting or fancy characters. Stick to plain text. "
            "If the user asks for a joke or a story, keep it short and clever. "
            "When asked for math or factual answers, give a direct answer and show your work briefly. "
            "Answer all questions to the best of your ability without asking follow-up questions."
        )

        print("📨 Incoming message:", incoming_msg)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": incoming_msg}
            ],
            max_tokens=300,
            temperature=0.7
        )

        reply = response.choices[0].message.content.strip() if response.choices[0].message.content else "No response"

    except Exception:
        reply = "Sorry, I'm having trouble processing your message right now. Please try again later."
        print("❌ Error occurred:")
        traceback.print_exc()

    messages.append({
        "incoming": incoming_msg,
        "reply": reply
    })

    twiml = MessagingResponse()
    twiml.message(reply)
    return str(twiml)

@app.route("/api/messages")
def get_messages():
    return jsonify({
        "messages": messages[-10:],  # Limit to last 10 messages
        "count": len(messages)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
