import os
from fastapi import APIRouter
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from database import get_connection

load_dotenv()
router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def gather_campus_snapshot():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT r.name AS room_id, b.name AS building_id, sr.occupancy, r.capacity,
               sr.temperature_c, sr.ac_status, sr.lighting_status, sr.power_kw, sr.is_anomaly
        FROM sensor_reading sr
        JOIN room r ON sr.room_id = r.id
        JOIN building b ON r.building_id = b.id
        WHERE sr.id IN (SELECT MAX(id) FROM sensor_reading GROUP BY room_id)
        ORDER BY sr.power_kw DESC
    """)
    rooms = cur.fetchall()

    cur.execute("""
        SELECT r.name AS room_id, rec.type, rec.reason, rec.proposed_action, rec.status
        FROM recommendation rec JOIN room r ON rec.room_id = r.id
        WHERE rec.status = 'PENDING'
        ORDER BY rec.created_at DESC LIMIT 20
    """)
    recommendations = cur.fetchall()

    cur.close()
    conn.close()
    return {"rooms": [dict(r) for r in rooms], "pending_recommendations": [dict(r) for r in recommendations]}


class AssistantQuery(BaseModel):
    question: str


@router.post("/assistant/ask")
def ask_assistant(query: AssistantQuery):
    snapshot = gather_campus_snapshot()

    system_prompt = (
        "You are a campus operations assistant for CampusTwin AI. "
        "You must answer ONLY using the data provided below. "
        "Never invent numbers, room names, or facts not present in the data. "
        "If the data doesn't contain the answer, say so honestly. "
        "Be concise and specific, citing room names and real numbers from the data.\n\n"
        "Prefer short paragraphs or simple bullet lists over markdown tables, since the chat UI displays plain text. "
        f"CURRENT ROOM DATA (all rooms, sorted by power consumption):\n{snapshot['rooms']}\n\n"
        f"PENDING RECOMMENDATIONS:\n{snapshot['pending_recommendations']}"
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query.question},
        ],
        max_tokens=600,
    )

    return {"question": query.question, "answer": response.choices[0].message.content}