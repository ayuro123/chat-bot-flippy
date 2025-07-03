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
    incoming_msg = request.form.get("Body", "")

    try:
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

        messages.append({
            "incoming": incoming_msg,
            "reply": reply
        })

        print(f"📩 Incoming SMS: {incoming_msg}")
        print(f"🤖 ChatGPT reply: {reply}")

    except Exception as e:
        reply = "Sorry, I'm having trouble processing your message right now. Please try again later."
        print("Error occurred:")
        traceback.print_exc()

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
