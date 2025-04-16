import pandas as pd

# --- Dosya İsimlerini Ayarla ---
input_file = "translated_skills.csv"            # Giriş CSV dosyanızın ismi
output_file = "skill_filled.csv"      # Çıktı dosyasının ismi

# --- CSV Dosyasını Oku ---
df = pd.read_csv(input_file)

# --- Boş Değerlerin Belirlenmesi ve Doldurulması ---
# "Turkce_Skill" sütununda tamamen boş ya da sadece boşluklardan oluşan değerleri pd.NA ile değiştir,
# ardından boş değerleri aynı satırdaki "Skill" sütunundaki verilerle doldur.
df.loc[:, 'Turkce_Skill'] = df['Turkce_Skill'].replace(r'^\s*$', pd.NA, regex=True)
df.loc[:, 'Turkce_Skill'] = df['Turkce_Skill'].fillna(df['Skill'])

# --- Güncellenmiş DataFrame'i Kaydet ---
df.to_csv(output_file, index=False)
print(f"Güncellenmiş CSV dosyası '{output_file}' olarak kaydedildi.")
