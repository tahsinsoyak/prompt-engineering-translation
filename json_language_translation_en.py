import json
import time
import os
from groq import Groq
from dotenv import load_dotenv

# --- Load environment variables and initialize Groq client ---
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- 1. Read the source JSON ---
input_file = "en.json"
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)  # :contentReference[oaicite:0]{index=0}&#8203;:contentReference[oaicite:1]{index=1}

# --- 2. Flatten nested dict into list of (path, text) ---
def flatten_dict(d, parent_key=""):
    items = []
    for k, v in d.items():
        path = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, str):
            items.append((path, v))
        elif isinstance(v, dict):
            items.extend(flatten_dict(v, path))
    return items

entries = flatten_dict(data)
print(f"Total strings to translate: {len(entries)}")

# --- 3. Chunk them ---
def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]

chunk_size = 50
chunks = list(chunk_list(entries, chunk_size))
print(f"Total chunks: {len(chunks)}")

# --- 4. Build a prompt that asks for JSON output ---
def create_prompt(chunk):
    """
    Asks the model to translate a list of Turkish UI strings into English.
    The model should return a JSON object mapping each path to its English translation.
    """
    lines = "\n".join(
        f"{i+1}. \"{path}\": \"{text}\"" for i, (path, text) in enumerate(chunk)
    )
    return f"""
You are a professional translator translating Turkish UI labels, buttons, and messages into natural, context‑aware English for a web application.

Please output a single valid JSON object mapping each key path to its English translation. Example output:

{{
  "homePage.welcome": "Welcome to the Academy!",
  "sidebar.homePage": "Home"
}}

Do not include any additional keys or commentary.

Here are the Turkish strings to translate:
{lines}
"""

# --- 5. Call Groq and collect translations ---
translations = {}
for idx, chunk in enumerate(chunks, start=1):
    prompt = create_prompt(chunk)
    print(f"Translating chunk {idx}/{len(chunks)}…")
    resp = client.chat.completions.create(
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
        messages=[
            {"role": "system", "content": "You are a translator specialized in website UI."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    text = resp.choices[0].message.content
    try:
        partial = json.loads(text)
        translations.update(partial)
    except json.JSONDecodeError:
        print(f"Warning: JSON parse error on chunk {idx}. Skipping.")
    time.sleep(5)  # rate limiting

# --- 6. Rebuild nested structure ---
def unflatten_dict(flat: dict):
    out = {}
    for path, eng in flat.items():
        keys = path.split(".")
        d = out
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = eng
    return out

output_data = unflatten_dict(translations)

# --- 7. Write English JSON ---
output_file = "yeni_translation_en.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"✅ Translated JSON saved to {output_file}")
print(f"Total entries translated: {len(translations)}")
