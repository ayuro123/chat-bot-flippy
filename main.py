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
    return "✅ SMS Chatbot is running."

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

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

    except Exception as e:
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
        "messages": messages[-10:],
        "count": len(messages)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
