from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI
import traceback

app = Flask(__name__)

client = OpenAI(api_key="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")

messages = []

@app.route("/")
def home():
    return "SMS Chatbot is running."

@app.route("/sms", methods=["POST"])
def sms_reply():
    from twilio.twiml.messaging_response import MessagingResponse
    twiml = MessagingResponse()
    twiml.message("✅ Flask is alive and responding.")
    return str(twiml)

@app.route("/api/messages")
def get_messages():
    return jsonify({
        "messages": messages[-10:],
        "count": len(messages)
    })

@app.route("/api/messages")
def get_messages():
    return jsonify({
        "messages": messages[-10:],
        "count": len(messages)
    })

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
