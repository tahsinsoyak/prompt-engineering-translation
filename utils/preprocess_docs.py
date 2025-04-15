import pandas as pd

# --- Dosya İsimlerini Ayarla ---
input_file = "merged_jobs.csv"    # Giriş CSV dosyanızın ismi
output_file = "final_jobs.csv"      # Çıkış dosyası ismi

# --- CSV Dosyasını Oku ---
df = pd.read_csv(input_file)

# --- Boş Değerlerin Belirlenmesi ve Doldurulması ---
# Turkce_Meslek sütununda, tamamen boş (ya da boşluklardan oluşan) değerleri pd.NA ile değiştir,
# ardından boş değerleri Job Titles_En sütunundaki veriyle doldur.
df.loc[:, 'Turkce_Meslek'] = df['Turkce_Meslek'].replace(r'^\s*$', pd.NA, regex=True)
df.loc[:, 'Turkce_Meslek'] = df['Turkce_Meslek'].fillna(df['Job Titles_En'])

# --- Güncellenmiş DataFrame'i Kaydet ---
df.to_csv(output_file, index=False)
print(f"Güncellenmiş CSV dosyası '{output_file}' olarak kaydedildi.")
