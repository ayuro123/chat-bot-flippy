"""
BACKUP - Working SMS Chatbot with OpenAI Only
Created: July 3, 2025
Status: Fully functional with Twilio integration

This is the original working version that uses only OpenAI GPT-3.5-turbo
without live data access. Keep this file as a backup to restore if needed.
"""

from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI

app = Flask(__name__)

# OpenAI API key (hardcoded as per original setup)
client = OpenAI(api_key="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")

# Store messages for web interface
messages = []

@app.route("/")
def home():
    """Web interface to view SMS messages and responses"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SMS Chatbot Monitor</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background-color: #ffffff;
                color: #333333;
            }
            .card {
                border: 1px solid #dee2e6;
                box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
            }
            .alert-info {
                background-color: #d1ecf1;
                border-color: #bee5eb;
                color: #0c5460;
            }
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
                    <div id="messages-container">
                        <!-- Messages will be loaded here -->
                    </div>
                </div>
            </div>
            <div class="mt-3">
                <button class="btn btn-primary" onclick="loadMessages()">Refresh Messages</button>
                <small class="text-muted ms-3">Auto-updating every 5 seconds</small>
            </div>
        </div>

        <script>
            function loadMessages() {
                fetch('/api/messages')
                    .then(response => response.json())
                    .then(data => {
                        const container = document.getElementById('messages-container');
                        
                        if (data.messages && data.messages.length > 0) {
                            container.innerHTML = '';
                            // Show messages in chronological order (oldest first, newest last)
                            data.messages.forEach(msg => {
                                const messageDiv = document.createElement('div');
                                messageDiv.className = 'alert alert-info mb-2';
                                messageDiv.innerHTML = `
                                    <strong>📩 Incoming:</strong> ${msg.incoming}<br>
                                    <strong>🤖 Reply:</strong> ${msg.reply}
                                `;
                                container.appendChild(messageDiv);
                            });
                        } else {
                            container.innerHTML = '<p class="text-muted">No messages yet. Send an SMS to start!</p>';
                        }
                    })
                    .catch(error => {
                        console.log('Loading messages...');
                    });
            }
            
            // Load messages when page loads
            loadMessages();
            
            // Auto-refresh every 5 seconds
            setInterval(loadMessages, 5000);
        </script>
    </body>
    </html>
    """
    return html

@app.route("/sms", methods=["POST"])
def sms_reply():
    """Handle incoming SMS messages and generate AI responses"""
    # Get the message body from Twilio
    incoming_msg = request.form.get("Body")
    
    try:
        # Generate response using OpenAI
        system_prompt = (
            "You are a highly intelligent and versatile AI assistant. "
            "You can explain advanced medical and scientific concepts, solve math problems, define words, "
            "tell jokes, answer trivia, describe locations, summarize news, provide recipes, and more. "
            "You are designed to respond over SMS, so your answers must be clear, concise, and readable on a basic phone screen. "
            "Avoid unnecessary formatting or fancy characters. Stick to plain text. If the user asks for a joke or a story, keep it short and clever. "
            "When asked for math or factual answers, give a direct answer and show your work briefly. "
            "Answer all questions to the best of your ability without asking follow-up questions."
        )

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
        
        # Store the conversation
        messages.append({
            "incoming": incoming_msg,
            "reply": reply
        })
        
        # Log to console for debugging
        print(f"📩 Incoming SMS: {incoming_msg}")
        print(f"🤖 ChatGPT reply: {reply}")
        
    import traceback

except Exception as e:
    reply = "Sorry, I'm having trouble processing your message right now. Please try again later."
    print("Error occurred:")
    traceback.print_exc()
    
    # Create Twilio response
    twiml = MessagingResponse()
    twiml.message(reply)
    
    return str(twiml)

@app.route("/api/messages")
def get_messages():
    """API endpoint to get recent messages"""
    return jsonify({
        "messages": messages[-10:],  # Return last 10 messages
        "count": len(messages)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
