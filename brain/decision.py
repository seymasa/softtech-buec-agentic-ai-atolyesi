from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-120b"

ROLE = """Sen yardımcı bir asistansın. Kullanıcının isteğini yerine getirmek \
için sana tanıtılan tool'ları kullan. Her adımda tek bir tool seç. \
Yapılacak iş kalmayınca tool seçme, kullanıcıya kısa bir Türkçe cevap yaz."""


def decide(memory, tool_schemas):
    system = {"role": "system", "content": ROLE}
    response = client.chat.completions.create(
        model=MODEL,
        messages=[system] + memory.messages,
        tools=tool_schemas,
        temperature=0,
    )
    message = response.choices[0].message

    if message.tool_calls:
        call = message.tool_calls[0].function
        return call.name, json.loads(call.arguments), None

    return None, None, message.content
