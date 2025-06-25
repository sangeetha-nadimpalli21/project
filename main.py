from fastapi import FastAPI, UploadFile, File, Form
import sqlite3, csv, io

app = FastAPI()

conn = sqlite3.connect("leads.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    status TEXT DEFAULT 'pending'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS call_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    timestamp TEXT,
    transcript TEXT,
    response TEXT,
    status TEXT
)
""")

conn.commit()

@app.post("/upload/")
async def upload_csv(file: UploadFile = File(...)):
    content = await file.read()
    reader = csv.reader(io.StringIO(content.decode("utf-8")))
    next(reader)
    for row in reader:
        name, phone = row
        cursor.execute("INSERT INTO leads (name, phone) VALUES (?, ?)", (name, phone))
    conn.commit()
    return {"message": "Leads uploaded successfully."}

@app.get("/next-lead/")
def next_lead():
    cursor.execute("SELECT * FROM leads WHERE status='pending' LIMIT 1")
    lead = cursor.fetchone()
    if lead:
        return {"id": lead[0], "name": lead[1], "phone": lead[2]}
    return {"message": "No leads left."}

@app.post("/update/{lead_id}")
def update_lead(lead_id: int, status: str = Form(...)):
    cursor.execute("UPDATE leads SET status=? WHERE id=?", (status, lead_id))
    conn.commit()
    return {"message": "Lead updated"}

from fastapi.responses import JSONResponse

@app.get("/transcripts/")
def get_transcripts():
    cursor.execute("SELECT * FROM call_logs")
    rows = cursor.fetchall()
    transcripts = []
    for row in rows:
        transcripts.append({
            "lead_id": row[1],
            "timestamp": row[2],
            "transcript": row[3],
            "response": row[4],
            "status": row[5]
        })
    return JSONResponse(content=transcripts)
