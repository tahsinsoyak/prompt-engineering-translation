import pandas as pd
from openai import OpenAI
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client with API key
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key= os.environ["OPENROUTER_API_KEY"],
)

# --- Step 1: Read the File ---
# Read the Excel file (use read_csv if applicable)
df = pd.read_excel("docs/jobs_part_15.xlsx")
# Assume the English job titles are in the column "Job Titles_En"
job_titles = df["Job Titles_En"].tolist()

# --- Step 2: Split the Job Titles into Chunks ---
def chunk_list(lst, chunk_size):
    """Splits the list into chunks of size chunk_size."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

# We'll send 30 job titles per API call (adjust as needed)
chunks = list(chunk_list(job_titles, 50))

# --- Step 3: Create the Prompt (in English) ---
def create_prompt(job_list):
    """
    Prepares the prompt to be sent to the Groq API.
    The prompt instructs to translate the given job titles into Turkish,
    using the Turkish job titles that are commonly used in Turkey.
    """
    job_lines = "\n".join([f"{i+1}. {job}" for i, job in enumerate(job_list)])
    prompt = f"""Below is a list of English job titles. Please translate each title into Turkish using the job titles that are widely recognized and appropriately sector-specific in Turkey.

For each job title, provide the answer in the following format:
English Job Title: Turkish Job Title
*DO NOT include any additional text or explanations.*
*DO NOT include any additional text.*
*DO NOT include any translations that are not commonly used in Turkey.*
For example:
Software Engineer: Yazılım Mühendisi

If there is no direct translation, provide the closest equivalent.
    
Job Titles:
{job_lines}
"""
    return prompt

# --- Step 4: Make the Groq API Call ---
# Note: The model has limits specified:
# meta-llama/llama-4-maverick-17b-128e-instruct  --> 30 requests per minute, etc.
def get_translations_for_chunk(chunk):
    """
    Calls the Groq API for a single chunk of job titles and returns the result.
    """
    prompt = create_prompt(chunk)
    
    try:
        response = client.chat.completions.create(
            model="openrouter/optimus-alpha",
            messages=[
                {"role": "system", "content": "You are a professional translator with expertise in the Turkish labor market and a deep understanding of sector-specific job titles."},
                {"role": "user", "content": prompt}
            ],
        )
        result_text = response.choices[0].message.content
        return result_text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

all_translations_text = []

# --- Step 5: Process each chunk with Rate Limiting ---
# To ensure maximum 30 requests per minute, each request must be spaced by at least 2 seconds.
for chunk in chunks:
    start_time = time.time()  # record the start time of the request
    result = get_translations_for_chunk(chunk)
    if result:
        all_translations_text.append(result)
    # Calculate the elapsed time; sleep for the remaining time to complete 2 seconds per request.
    elapsed = time.time() - start_time
    sleep_duration = max(2 - elapsed, 0)
    time.sleep(sleep_duration)

# --- Step 6: Parse the API Responses ---
def parse_translations(response_text):
    """
    Parses the API response text line by line and extracts translations
    that follow the 'English Job Title: Turkish Job Title' format into a dictionary.
    """
    translations_dict = {}
    lines = response_text.splitlines()
    for line in lines:
        if ":" in line:
            parts = line.split(":", 1)
            eng_title = parts[0].strip()
            tr_title = parts[1].strip()
            # Clean up number prefixes if present (e.g., "1. Software Engineer")
            if ". " in eng_title:
                eng_title = eng_title.split(". ", 1)[1]
            translations_dict[eng_title] = tr_title
    return translations_dict

# Combine translations from all chunks
translations_all = {}
for chunk_response in all_translations_text:
    parsed = parse_translations(chunk_response)
    translations_all.update(parsed)

# --- Step 7: Merge the Translations with the Original Data and Save ---
# Map the translations to the original DataFrame using the "Job Titles_En" column
df["Turkce_Meslek"] = df["Job Titles_En"].map(translations_all)

# Save the resulting DataFrame to a new CSV file
df.to_csv("jobs_part_15.csv", index=False)
print("Translations saved successfully in jobs_part_11.csv")
