import os
import pandas as pd
import re

# --- Step 1: Create a Function to Load the File (CSV or XLSX) ---
def load_file(filename, text_column='Skill'):
    """
    Loads a file (CSV or XLSX) into a Pandas DataFrame.
    Raises a ValueError if the file format is not supported.
    """
    ext = os.path.splitext(filename)[1].lower()  # Get file extension in lowercase
    if ext == ".csv":
        df = pd.read_csv(filename)
    elif ext in [".xls", ".xlsx"]:
        df = pd.read_excel(filename)
    else:
        raise ValueError("Unsupported file format: " + ext)
    
    # Check if the expected text column exists.
    if text_column not in df.columns:
        raise ValueError(f"Column '{text_column}' not found in the file!")
    return df

# --- Step 2: Define Functions to Count Letters and Words ---
def count_letters(text):
    """
    Counts the number of alphabetic characters in a text.
    Only letters (a-z, A-Z) are considered.
    """
    if isinstance(text, str):
        return sum(1 for char in text if char.isalpha())
    return 0

def count_words(text):
    """
    Counts the number of words in a text by splitting on whitespace.
    This assumes that words are separated by spaces.
    """
    if isinstance(text, str):
        words = text.split()  # Split the text by whitespace.
        return len(words)
    return 0

# --- Step 3: Process the DataFrame ---
def process_file(filename, text_column='Skill'):
    """
    Loads the file, applies letter and word count functions,
    prints the total counts, and returns the DataFrame with added columns.
    """
    df = load_file(filename, text_column)
    df['letter_count'] = df[text_column].apply(count_letters)
    df['word_count'] = df[text_column].apply(count_words)
    
    # Calculate totals across the DataFrame.
    total_letters = df['letter_count'].sum()
    total_words = df['word_count'].sum()
    
    print(f"For {filename}:")
    print("Total letters:", total_letters)
    print("Total words:", total_words)
    return df

# --- Example Usage ---

# Process a CSV file.
csv_filename = 'skills.csv'
df_csv = process_file(csv_filename)

# Process an Excel file.
xlsx_filename = 'jobs.xlsx'
df_xlsx = process_file(xlsx_filename, text_column='Job Titles_En')

# Optionally, you can save the processed DataFrame with the new columns to a new file.
# df_csv.to_csv('processed_skills_csv.csv', index=False)
# df_xlsx.to_excel('processed_skills_xlsx.xlsx', index=False)
