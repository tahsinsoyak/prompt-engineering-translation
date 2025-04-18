import json
import time
import os
from groq import Groq
from dotenv import load_dotenv

# --- Load environment variables and initialize Groq client ---
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- 1. Read the source JSON of Turkish UI strings ---
input_file = "translation.json"
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

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

# --- 3. Chunk them for API calls ---
def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]

chunk_size = 50
chunks = list(chunk_list(entries, chunk_size))
print(f"Total chunks: {len(chunks)}")

# --- 4. Build a prompt asking for Azerbaijani output in JSON ---
def create_prompt(chunk):
    """
    Asks the model to translate Turkish UI strings into natural, context‑aware Azerbaijani.
    The model should return a single valid JSON object mapping each path to its Azerbaijani translation.
    """
    lines = "\n".join(
        f"{i+1}. \"{path}\": \"{text}\"" for i, (path, text) in enumerate(chunk)
    )
    return f"""
Siz veb tətbiqin UI etiketi, düymə yazısı və mesajlarını **məzmun kontekstində** təbii Azərbaycan dilinə tərcümə edən peşəkar tərcüməçisiniz.

Xahiş olunur, yalnız **tək bir düzgün JSON** obyektini qaytarın, açar – yol (məs. "homePage.welcome"), dəyər – Azərbaycan dilində tərcümə. Məsələn:

{{
  "homePage.welcome": "Akademiyaya xoş gəlmisiniz!",
  "sidebar.homePage": "Ana səhifə"
}}

Əlavə açarlar və ya şərhlər daxil etməyin.

Aşağıdakı Türkçe UI yazılarını tərcümə edin:
{lines}
"""

# --- 5. Call Groq and collect Azerbaijani translations ---
translations = {}
for idx, chunk in enumerate(chunks, start=1):
    prompt = create_prompt(chunk)
    print(f"Translating chunk {idx}/{len(chunks)}…")
    resp = client.chat.completions.create(
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
        messages=[
            {"role": "system", "content": "Siz veb UI üçün ixtisaslaşmış tərcüməçisiniz."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    text = resp.choices[0].message.content
    try:
        partial = json.loads(text)
        translations.update(partial)
    except json.JSONDecodeError:
        print(f"⚠️ JSON parse error on chunk {idx}. Skipping.")
    time.sleep(5)  # pause to respect rate limits

# --- 6. Rebuild the nested structure from flattened paths ---
def unflatten_dict(flat: dict):
    out = {}
    for path, az in flat.items():
        keys = path.split(".")
        d = out
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = az
    return out

output_data = unflatten_dict(translations)

# --- 7. Write out the Azerbaijani JSON ---
output_file = "translation_az.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"✅ Azerbaijani JSON saved to {output_file}")
print(f"Total entries translated: {len(translations)}")
