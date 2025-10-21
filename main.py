from fastapi import FastAPI, Request, Response
from openai import OpenAI
from elevenlabs import ElevenLabs
import os
import tempfile

app = FastAPI()

# -------------------------------------------------------
# Load environment variables
# -------------------------------------------------------
EXOTEL_SID = os.getenv("EXOTEL_SID")
EXOTEL_API_KEY = os.getenv("EXOTEL_API_KEY")
EXOTEL_TOKEN = os.getenv("EXOTEL_TOKEN")
EXOPHONE = os.getenv("EXOPHONE")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY")

openai_client = OpenAI(api_key=OPENAI_KEY)
eleven_client = ElevenLabs(api_key=ELEVEN_KEY)

# -------------------------------------------------------
# MAIN EXOTEL CALLBACK ROUTE
# -------------------------------------------------------
@app.post("/exotel-ai")
async def exotel_ai(request: Request):
    """
    Called by Exotel when a call is connected.
    It generates a greeting message and returns XML with a playable audio URL.
    """

    # 1️⃣ Generate AI text
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a polite AI sales agent for Singh Associates."},
            {"role": "user", "content": "Create a short, friendly greeting pitch for agrochemical logistics services."}
        ]
    )
    reply_text = completion.choices[0].message.content.strip()

    # 2️⃣ Convert text to voice using ElevenLabs
    try:
        audio_data = eleven_client.text_to_speech.convert(
            voice_id="Aditi",
            model_id="eleven_turbo_v2",
            text=reply_text
        )
        temp_path = tempfile.mktemp(suffix=".mp3")
        with open(temp_path, "wb") as f:
            f.write(audio_data)

        # 🔊 Play your hosted ElevenLabs audio (LimeWire link)
        public_url = "https://limewire.com/d/tMtE7#U0DbrTTiXe"

    except Exception as e:
        # In case ElevenLabs fails, fall back to demo audio
        print("Error generating audio:", e)
        public_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

    # 3️⃣ Send XML response to Exotel
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{public_url}</Play>
</Response>"""

    return Response(content=xml, media_type="text/xml")


# -------------------------------------------------------
# TEST ROUTE (for Browser / Exotel validation)
# -------------------------------------------------------
@app.get("/exotel-ai-test")
def exotel_test():
    """
    Simple GET route that returns sample XML.
    Use this to test Exotel passthru connection.
    """
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3</Play>
</Response>"""
    return Response(content=xml, media_type="text/xml")


# -------------------------------------------------------
# HEALTH CHECK ROUTE
# -------------------------------------------------------
@app.get("/")
def home():
    return {"message": "AI Voice Agent is running!"}
