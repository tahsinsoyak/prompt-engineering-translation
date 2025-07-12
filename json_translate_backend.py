import json
import time
import os
import re
from groq import Groq
from dotenv import load_dotenv

# --- Load environment variables and initialize Groq client ---
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- 1. Read the source JSON with "data" list ---
input_file = "source_data_backend.json"
with open(input_file, "r", encoding="utf-8") as f:
    raw = json.load(f)

# --- 2. Extract list of (key, text) pairs from the "data" array ---
entries = []
for item in raw.get("data", []):
    key = item.get("_name")
    text = item.get("value")
    if key and isinstance(text, str):
        entries.append((key, text))

print(f"Total strings to translate: {len(entries)}")

# --- 3. Chunk them for API calls ---
def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]

chunk_size = 50  # Adjust if needed; 50 seems fine but can be tuned
chunks = list(chunk_list(entries, chunk_size))
print(f"Total chunks: {len(chunks)}")

# --- 4. Build a prompt that asks for JSON output mapping each _name to its translation ---
def create_prompt(chunk):
    lines = "\n".join(
        f"{i+1}. \"{key}\": \"{text}\"" for i, (key, text) in enumerate(chunk)
    )
    return f"""
You are a professional translator translating Turkish UI labels, buttons, and messages into natural, context-aware English for a web application called "Academy" that provides educational content. The translations should read naturally for a modern, user-friendly interface.

Please output a single valid JSON object mapping each key (_name) to its English translation. Example output:
{{
  "AbsentDuration": "Time Absent From Course",
  "AccessDate": "Date of Access"
}}

Do not include any additional keys, commentary, or markdown (e.g., ```json). Output only the JSON object with proper formatting.

*Do not use the word "Training" in translations; use "Course" instead.*

Here are the Turkish strings to translate (each key: value pair):
{lines}
"""

# --- 5. Clean response to ensure valid JSON ---
def clean_json_response(text):
    # Remove markdown code fences and any leading/trailing text
    text = re.sub(r'^```json\s*|\s*```$', '', text, flags=re.MULTILINE)
    text = text.strip()
    # Ensure the response starts with { and ends with }
    if text.startswith('{') and text.endswith('}'):
        return text
    return None

# --- 6. Call Groq and collect translations ---
translations = {}
for idx, chunk in enumerate(chunks, start=1):
    prompt = create_prompt(chunk)
    print(f"Translating chunk {idx}/{len(chunks)}…")
    try:
        resp = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {"role": "system", "content": "You are a translator specialized in website UI."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        text = resp.choices[0].message.content
        cleaned_text = clean_json_response(text)
        if not cleaned_text:
            print(f"Warning: Invalid JSON format in chunk {idx}. Response was:\n{text}\nSkipping this chunk.")
            continue
        try:
            partial = json.loads(cleaned_text)
            if not isinstance(partial, dict):
                print(f"Warning: Response is not a JSON object in chunk {idx}. Response was:\n{text}\nSkipping this chunk.")
                continue
            translations.update(partial)
        except json.JSONDecodeError as e:
            print(f"Warning: JSON parse error on chunk {idx}. Response was:\n{text}\nError: {e}\nSkipping this chunk.")
    except Exception as e:
        print(f"Error during API call for chunk {idx}: {e}\nSkipping this chunk.")
    time.sleep(5)  # Rate limiting

print(f"Total entries translated: {len(translations)}")

# --- 7. Inject translations back into the raw structure ---
for item in raw.get("data", []):
    key = item.get("_name")
    if key in translations:
        item["value"] = translations[key]

# --- 8. Write the new JSON with translated "value" fields ---
output_file = "backend_translated_data.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(raw, f, ensure_ascii=False, indent=2)
    print(f"✅ Translated JSON saved to {output_file}")