import pandas as pd
from groq import Groq
import time
import os
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

# Groq client'ı API anahtarı ile başlat
client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

# --- Dosya İsimlerini Değişken Olarak Belirle ---
input_filename = "docs/jobs_part_15.xlsx"   # Giriş dosya ismi
output_filename = "docs_translated/jobs_part_15.csv"  # Çıkış dosya ismi

# --- Adım 1: Dosyayı Oku ---
# Giriş dosyasını oku. (Gerekirse read_csv kullanabilirsiniz)
df = pd.read_excel(input_filename)
# Excel dosyanızda İngilizce iş tanımları "Job Titles_En" sütununda yer alıyor varsayılıyor.
job_titles = df["Job Titles_En"].tolist()

# --- Adım 2: İş Tanımlarını Parçalara Böl ---
def chunk_list(lst, chunk_size):
    """Verilen listeyi, chunk_size büyüklüğünde parçalara böler."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

# Her API çağrısında 50 iş tanımı göndereceğiz (gereksinimlerinize göre ayarlayabilirsiniz)
chunks = list(chunk_list(job_titles, 50))

# --- Adım 3: API için Prompt'u Oluştur ---
def create_prompt(job_list):
    """
    Groq API'sine gönderilecek prompt metnini hazırlar.
    İngilizce iş tanımlarını, Türkiye'de yaygın kullanılan Türkçe karşılıklarına çevirmesini ister.
    """
    job_lines = "\n".join([f"{i+1}. {job}" for i, job in enumerate(job_list)])
    prompt = f"""Below is a list of English job titles. Please translate each title into Turkish using the job titles that are widely recognized and appropriately sector-specific in Turkey.

For each job title, provide the answer in the following format:
English Job Title: Turkish Job Title
*DO NOT include any additional text or explanations!!!.*
*DO NOT include any additional text or explanations!!!.*
*DO NOT include any additional text or explanations!!!.*
*DO NOT include any translations that are not commonly used in Turkey.*
*IF YOU ARE NOT SURE ABOUT A TRANSLATION, PLEASE LEAVE IT BLANK.*
For example:
Software Engineer: Yazılım Mühendisi

If there is no direct translation, provide the closest equivalent.
    
Job Titles:
{job_lines}
"""
    return prompt

# --- Adım 4: Groq API Çağrısını Yap ---
def get_translations_for_chunk(chunk):
    """
    Belirtilen iş tanımları parçası için Groq API çağrısı yapar ve sonucu döndürür.
    """
    prompt = create_prompt(chunk)
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",  # Groq API tarafından desteklenen model adı
            messages=[
                {"role": "system", "content": "You are a professional translator with expertise in the Turkish labor market and a deep understanding of sector-specific job titles."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # Düşük sıcaklık, tutarlı sonuçlar için
        )
        result_text = response.choices[0].message.content
        return result_text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

all_translations_text = []

# --- Adım 5: Her Parça İçin İşlemi Rate Limit'e Uygun Olarak Gerçekleştir ---
# API'nin dakikada 30 isteğe izin vermesi göz önüne alındığında, her istek arasında en az 2 saniye bekleme uygulanıyor.
for chunk in chunks:
    start_time = time.time()  # İstek başlangıç zamanını kaydet
    result = get_translations_for_chunk(chunk)
    if result:
        all_translations_text.append(result)
    # Geçen süreyi hesapla; 2 saniyenin tamamlanması için kalan süreyi bekle.
    elapsed = time.time() - start_time
    sleep_duration = max(2 - elapsed, 0)
    time.sleep(sleep_duration)

# --- Adım 6: API Yanıtlarını Ayrıştır ---
def parse_translations(response_text):
    """
    API yanıtı metnini satır satır inceleyerek
    'English Job Title: Turkish Job Title' formatına uygun çevirileri bir sözlüğe aktarır.
    """
    translations_dict = {}
    lines = response_text.splitlines()
    for line in lines:
        if ":" in line:
            parts = line.split(":", 1)
            eng_title = parts[0].strip()
            tr_title = parts[1].strip()
            # Numara ile başlayan önekleri temizle (örn. "1. Software Engineer")
            if ". " in eng_title:
                eng_title = eng_title.split(". ", 1)[1]
            translations_dict[eng_title] = tr_title
    return translations_dict

# Tüm parçaların çeviri sonuçlarını birleştir
translations_all = {}
for chunk_response in all_translations_text:
    parsed = parse_translations(chunk_response)
    translations_all.update(parsed)

# --- Adım 7: Çevirileri Orijinal Veriyle Birleştir ve Kaydet ---
# "Job Titles_En" sütununa göre eşleştirme yapılır.
df["Turkce_Meslek"] = df["Job Titles_En"].map(translations_all)

# Sonuçları output_filename'de belirtilen dosyaya CSV olarak kaydet
df.to_csv(output_filename, index=False)
print(f"Translations saved successfully in {output_filename}")
