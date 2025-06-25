import requests
import sqlite3
from datetime import datetime
from transformers import pipeline

# Use a cleaner, more relevant model
chatbot = pipeline("text-generation", model="sshleifer/tiny-gpt2")

BACKEND_URL = "http://127.0.0.1:8000"

def get_next_lead():
    try:
        res = requests.get(f"{BACKEND_URL}/next-lead/")
        if res.status_code == 200 and "id" in res.json():
            return res.json()
        else:
            return None
    except Exception as e:
        print(f"🚫 Error fetching lead: {e}")
        return None

def update_status(lead_id, status):
    try:
        requests.post(f"{BACKEND_URL}/update/{lead_id}", data={"status": status})
    except Exception as e:
        print(f"⚠️ Error updating lead status: {e}")

def log_transcript(lead_id, transcript, response, status):
    try:
        conn = sqlite3.connect("leads.db")
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO call_logs (lead_id, timestamp, transcript, response, status)
            VALUES (?, ?, ?, ?, ?)
        """, (lead_id, timestamp, transcript, response, status))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ Error logging transcript: {e}")

def simulate_chat_with_lead(lead):
    name = lead['name']
    phone = lead['phone']
    lead_id = lead['id']

    print(f"\n📞 Chatting with: {name} ({phone})")

    prompt = f"The customer {name} asked: Can I know more about your restaurant products?"

    try:
        result = chatbot(prompt, max_length=50, num_return_sequences=1)
        reply = result[0]['generated_text'].strip()
    except Exception as e:
        print("❌ HuggingFace error:", str(e))
        return

    # Clean up the chatbot's reply
    reply_clean = reply.split(".")[0] + "." if "." in reply else reply.strip()

    # Status logic
    response_lower = reply_clean.lower()
    if "yes" in response_lower or "interested" in response_lower:
        status = "interested"
    elif "no" in response_lower or "not interested" in response_lower:
        status = "not interested"
    else:
        status = "neutral"

    # Format the transcript
    transcript = f"Bot: Would you like our catalog?\n{name}: {reply_clean}"
    print("📜 Transcript:\n" + transcript)
    print(f"✅ Status: {status}")

    # Log and update
    log_transcript(lead_id, transcript, reply_clean, status)
    update_status(lead_id, status)

if __name__ == "__main__":
    lead = get_next_lead()
    if lead:
        simulate_chat_with_lead(lead)
    else:
        print("🚫 No pending leads found.")
