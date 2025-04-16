import pandas as pd
from groq import Groq
import time
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Initialize Groq client with API key
client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

# --- Step 1: Read the CSV File ---
# Assumes your CSV file (e.g., "skills.csv") contains a column with the English skills.
input_filename = "skills.csv"  # Change this if needed
df = pd.read_csv(input_filename)
# Change "Skill" to the actual column name that contains the skills
skills = df["Skill"].tolist()

# --- Step 2: Split the Skills into Chunks ---
def chunk_list(lst, chunk_size):
    """Splits the list into chunks of size chunk_size."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

# In this example, we use 150 skills per API call.
chunks = list(chunk_list(skills, 150))
print(f"Total chunks: {len(chunks)}")

# --- Step 3: Create the Prompt (in English) ---
def create_prompt(skill_list):
    """
    Prepares the prompt to be sent to the Groq API.
    The prompt instructs the model to translate each English skill into Turkish.
    
    Instructions:
      - Provide the translation in the following format:
            English Skill: Turkish Skill
      - DO NOT include any additional text or explanations.
      - If the term represents a programming language, framework, tool, or software product,
        do not translate it – leave the term unchanged.
      - If you are not sure about a translation, please leave it blank.
      
    For example:
      cooking: aşçılık
      painting: resim sanatı
      programming: programlama
      data analysis: veri analizi
      management: yönetim
      marketing: pazarlama
      sales: satış
      python: python
      java: java
      WordPress: WordPress
      
    Skills:
    """
    # List each skill with a number prefix
    skill_lines = "\n".join([f"{i+1}. {skill}" for i, skill in enumerate(skill_list)])
    prompt = f"""Below is a list of English skills. Please translate each skill into Turkish using the widely recognized Turkish equivalent.
    
For each skill, provide the answer in the following format:
English Skill: Turkish Skill
*DO NOT include any additional text or explanations.*
*DO NOT include any translations that are not commonly used in Turkey.*
*IF THE TERM IS A PROGRAMMING LANGUAGE, FRAMEWORK, TOOL, OR SOFTWARE PRODUCT, DO NOT TRANSLATE IT (LEAVE IT UNCHANGED).*
*IF YOU ARE NOT SURE ABOUT A TRANSLATION, PLEASE LEAVE IT BLANK.*

For example:
Cooking: Aşçılık
painting: resim sanatı
programming: programlama
data analysis: veri analizi
Management: Yönetim
marketing: pazarlama
sales: satış
python: python
java: java
WordPress: WordPress

Skills:
{skill_lines}
"""
    return prompt

# --- Step 4: Make the Groq API Call ---
def get_translations_for_chunk(chunk):
    """
    Calls the Groq API for a single chunk of skills and returns the result text.
    """
    prompt = create_prompt(chunk)
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",  # Using the most capable translation model
            messages=[
                {"role": "system", "content": "You are a professional translator with expertise in the Turkish labor market, especially in translating technical and skill-related terms."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # Lower temperature for consistent results
        )
        result_text = response.choices[0].message.content
        return result_text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# --- Step 5: Parse the API Responses ---
def parse_translations(response_text):
    """
    Parses the API response text line by line and extracts translations
    in the format 'English Skill: Turkish Skill' into a dictionary.
    """
    translations_dict = {}
    lines = response_text.splitlines()
    for line in lines:
        if ":" in line:
            parts = line.split(":", 1)
            eng_skill = parts[0].strip()
            tr_skill = parts[1].strip()
            # Remove any numbering if present (e.g., "1. driving")
            if ". " in eng_skill:
                eng_skill = eng_skill.split(". ", 1)[1]
            translations_dict[eng_skill] = tr_skill
    return translations_dict

# --- Step 6: Process Each Chunk with Rate Limiting and Incremental CSV Update ---
output_filename = "translated_skills.csv"
translations_all = {}  # Global dictionary to store all translations

# Record overall start time for the entire translation process
overall_start_time = time.time()

for i, chunk in enumerate(chunks):
    chunk_start_time = time.time()
    print(f"Processing chunk {i+1}/{len(chunks)}")
    result = get_translations_for_chunk(chunk)
    if result:
        parsed_chunk = parse_translations(result)
        translations_all.update(parsed_chunk)
    # Respect API rate limits: wait at least 5 seconds per request
    elapsed = time.time() - chunk_start_time
    sleep_duration = max(5 - elapsed, 0)
    time.sleep(sleep_duration)
    
    # Update the DataFrame with translations processed so far
    df["Turkce_Skill"] = df["Skill"].map(translations_all)
    # Save the current progress to the CSV file
    df.to_csv(output_filename, index=False)
    print(f"Updated CSV saved after chunk {i+1} in {output_filename}")

# Calculate total elapsed time
total_time = time.time() - overall_start_time

# Calculate total letters translated (sum of characters in all Turkish translations)
total_letters = sum(len(tr) for tr in translations_all.values() if tr)

# Print summary results
print(f"\nTüm çeviri işlemi tamamlandı.")
print(f"Toplam süre: {total_time:.2f} saniye")
print(f"Toplamda çevrilen harf sayısı: {total_letters}")
print("Kullanılan çeviri çevrimi: 150'şer skill'lık chunk'lar halinde, for-loop ile işlem yapıldı.")

print(f"All translations saved successfully in {output_filename}")
