from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv(override=True)
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

completion = client.chat.completions.create(
    model=os.getenv("MODEL_NAME"),
    messages=[
        {
            "role": "user",
            "content": "Hãy code một đoạn code python tính số fibonacci thứ 10"
        }
    ], 
    temperature=0.5,
    stream=True
)

for chunk in completion:
    print(chunk.choices[0].delta.content, end="", flush=True)