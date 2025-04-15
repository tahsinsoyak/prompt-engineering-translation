# Prompt Engineering Translation

## Project Description
The Prompt Engineering Translation project is designed to facilitate the translation of job titles and descriptions using advanced AI models. It leverages APIs to process and translate large datasets efficiently.

## Features
- Batch processing of job titles from Excel files.
- Integration with Groq and OpenAI APIs for translation.
- Environment variable management for secure API key handling.
- Modular code structure for easy maintenance and extension.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/tahsinsoyak/prompt-engineering-translation.git
   cd prompt-engineering-translation
   ```

2. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Create a `.env` file in the root directory.
   - Add your API keys:
     ```
     GROQ_API_KEY=your_groq_api_key
     OPENROUTER_API_KEY=your_openrouter_api_key
     ```

## Usage

1. **Preprocess Documents:**
   - Use `preprocess_docs.py` to clean and prepare your CSV files for translation.

2. **Split Documents:**
   - Use `split_doc.py` to divide large Excel files into manageable chunks.

3. **Translate Job Titles:**
   - Use `groq_api.py` or `openrouter_api.py` to translate job titles using the respective API.

4. **Merge Translated Files:**
   - Use `merge_doc.py` to combine translated files into a single CSV.

5. **Ensure Unique Job Titles:**
   - Use `unique_jobs.py` to make job titles unique.

## Folder Structure

```
prompt-engineering-translation/
│
├── utils/
│   ├── utils/split_doc.py          # Splits large Excel files into smaller chunks.
│   ├── utils/merge_doc.py          # Merges multiple CSV files into one.
│   ├── utils/preprocess_docs.py    # Prepares and cleans data for translation.
│   ├── utils/unique_jobs.py        # Ensures job titles are unique.
│
├── openrouter_api.py               # Handles translation using OpenRouter API.
├── groq_api.py                     # Handles translation using Groq API.
├── docs/                           # Contains input Excel files.
├── docs_translated/                # Contains translated CSV files.
├── .env                            # Stores API keys and environment variables.
└── README.md                       # Project documentation.
```

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## Contact
For any questions or feedback, please contact [tahsinsoyakk@gmail.com].
