from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI
import openai
import os
import traceback
import requests
from datetime import datetime

print("🔍 OpenAI version:", openai.__version__)

# ✅ Load API key from environment variable
openai_api_key = os.environ.get("OPENAI_API_KEY")
print("🔐 Loaded OPENAI_API_KEY from environment:", openai_api_key[:8] + "..." if openai_api_key else "❌ None FOUND")

# ✅ Create OpenAI client
client = OpenAI(api_key=openai_api_key)

# ✅ Flask app setup
app = Flask(__name__)
messages = []

@app.route("/")
def home():
    html = """<!DOCTYPE html>
    <html><head><title>SMS Chatbot Monitor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>body{background:#fff;color:#333}.card{border:1px solid #dee2e6;box-shadow:0 .125rem .25rem rgba(0,0,0,.075)}.alert-info{background:#d1ecf1;border-color:#bee5eb;color:#0c5460}</style>
    </head><body><div class="container mt-4">
    <h1 class="mb-4">📱 SMS Chatbot Monitor</h1>
    <div class="card"><div class="card-header bg-light"><h5 class="mb-0">Recent Messages</h5></div>
    <div class="card-body"><div id="messages-container"></div></div></div>
    <div class="mt-3"><button class="btn btn-primary" onclick="loadMessages()">Refresh</button>
    <small class="text-muted ms-3">Auto-refreshing every 5 seconds</small></div></div>
    <script>
    function loadMessages(){
        fetch('/api/messages').then(res=>res.json()).then(data=>{
            const c=document.getElementById('messages-container');c.innerHTML='';
            data.messages.forEach(msg=>{
                const d=document.createElement('div');
                d.className='alert alert-info mb-2';
                d.innerHTML=`<strong>📩 Incoming:</strong> ${msg.incoming}<br><strong>🤖 Reply:</strong> ${msg.reply}`;
                c.appendChild(d);
            });
        });
    }
    loadMessages(); setInterval(loadMessages,5000);
    </script></body></html>"""
    return html

@app.route("/sms", methods=["POST"])
def sms_reply():
    incoming_msg = request.form.get("Body", "").strip()
    twiml = MessagingResponse()

    # ✅ Check for Zmanim request
    if incoming_msg.lower().startswith("zmanim "):
        location = incoming_msg[7:].strip()
        try:
            today = datetime.today().strftime("%Y-%m-%d")
            url = f"https://www.hebcal.com/zmanim?cfg=json&geoname={location}&date={today}"
            res = requests.get(url)
            if res.status_code == 200:
                data = res.json()
                times = data["times"]

                is_friday = datetime.today().weekday() == 4
                reply = (
                    f"📆 Zmanim for {data['title']} ({today}):\n"
                    f"🕓 Alos (72): {times.get('alos72')}\n"
                    f"🌅 Netz: {times.get('sunrise')}\n"
                    f"🕘 Shema (Gra): {times.get('sofZmanShma')}\n"
                    f"🕘 Shema (MA): {times.get('sofZmanShmaMGA')}\n"
                    f"🕤 Tefillah: {times.get('sofZmanTfilla')}\n"
                    f"🕛 Chatzos: {times.get('chatzot')}\n"
                    f"⏰ Mincha Gedola: {times.get('minchaGedola')}\n"
                    f"⏰ Mincha Ketana: {times.get('minchaKetana')}\n"
                    f"🌇 Shkiah: {times.get('sunset')}\n"
                    f"🌃 Tzeis (72): {times.get('tzeit72')}"
                )
                if is_friday:
                    reply += f"\n🕯️ Hadlakas Neiros: {times.get('candle_lighting', 'N/A')}"
            else:
                reply = "❌ Could not fetch Zmanim. Try a ZIP code or city/state."
        except Exception:
            reply = "⚠️ Zmanim error. Try again."
    else:
        try:
            # ✅ Full system prompt for ChatGPT
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
            reply = response.choices[0].message.content.strip()
        except Exception:
            reply = "Sorry, I'm having trouble processing your message right now. Please try again later."
            print("❌ Error occurred:")
            traceback.print_exc()

    messages.append({"incoming": incoming_msg, "reply": reply})
    twiml.message(reply)
    return str(twiml)

@app.route("/api/messages")
def get_messages():
    return jsonify({
        "messages": messages[-10:],  # Limit to last 10
        "count": len(messages)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
