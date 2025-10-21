from fastapi import FastAPI, Request, Response
from openai import OpenAI
from elevenlabs import ElevenLabs
import requests, tempfile, os

app = FastAPI()

# 🔑 Read your API keys from environment variables later on Render
EXOTEL_SID = os.getenv("EXOTEL_SID")
EXOTEL_API_KEY = os.getenv("EXOTEL_API_KEY")
EXOTEL_TOKEN = os.getenv("EXOTEL_TOKEN")
EXOPHONE = os.getenv("EXOPHONE")  # your Exophone number
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY")

openai_client = OpenAI(api_key=OPENAI_KEY)
eleven_client = ElevenLabs(api_key=ELEVEN_KEY)

# --- Trigger outbound call ---
def make_outbound_call(customer_number):
    url = f"https://api.exotel.com/v1/Accounts/{EXOTEL_SID}/Calls/connect"
    data = {
        "From": EXOPHONE,
        "To": customer_number,
        "CallerId": EXOPHONE,
        "CallType": "trans",
        "Url": f"https://yourapp.onrender.com/exotel-ai"
    }
    response = requests.post(url, data=data, auth=(EXOTEL_API_KEY, EXOTEL_TOKEN))
    return response.text

# --- Exotel webhook ---
@app.post("/exotel-ai")
async def exotel_ai(request: Request):
    form = await request.form()
    caller = form.get("To") or form.get("From")

    completion = openai_client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "You are a polite sales agent from Singh Associates selling logistics services to agrochemical companies."},
            {"role": "user", "content": f"Create a friendly short pitch for caller {caller}."}
        ]
    )
    reply_text = completion.choices[0].message.content

    # Convert reply to speech
    audio_data = eleven_client.text_to_speech.convert(
        voice_id="Aditi",
        model_id="eleven_turbo_v2",
        text=reply_text
    )

    temp_path = tempfile.mktemp(suffix=".mp3")
    with open(temp_path, "wb") as f:
        f.write(audio_data)
    public_url = f"https://yourcdn.com/{os.path.basename(temp_path)}"

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{public_url}</Play>
</Response>"""
    return Response(content=xml, media_type="text/xml")

@app.get("/demo-call/{number}")
def demo_call(number: str):
    return make_outbound_call(number)
