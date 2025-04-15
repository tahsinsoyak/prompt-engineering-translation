import pandas as pd

# --- Dosya İsimlerini Ayarla ---
input_file = "final_jobs.csv"             # Giriş dosyası (önceki adımlarla oluşturulan dosya)
output_file = "final_jobs_unique.csv"     # Benzersiz sonuçların kaydedileceği dosya

# --- CSV Dosyasını Oku ---
df = pd.read_csv(input_file)

# --- Boş Değerleri Doldur ---
# Turkce_Meslek sütunundaki tamamen boş ya da sadece boşluklardan oluşan değerleri pd.NA yap,
# ardından boş olanlara Job Titles_En'deki değeri ata.
df.loc[:, 'Turkce_Meslek'] = df['Turkce_Meslek'].replace(r'^\s*$', pd.NA, regex=True)
df.loc[:, 'Turkce_Meslek'] = df['Turkce_Meslek'].fillna(df['Job Titles_En'])

# Orijinal değerlerin yedeğini oluşturuyoruz (benzersizleştirme sırasında diğer kolondaki orijinal değeri kullanmak için)
en_original = df["Job Titles_En"].copy()
tr_original = df["Turkce_Meslek"].copy()

def make_unique_with_counterpart(series, counterpart):
    """
    Verilen pandas Serisi içerisindeki tekrarlanan değerleri, 
    o satırın counterpart (karşı) kolonundaki orijinal değeri parantez içinde ekleyerek benzersiz hale getirir.
    Eğer eklenmiş değer de tekrar ederse, ek olarak sayısal bir ek ekler.
    """
    seen = {}          # Daha önce oluşmuş benzersiz değerleri izlemek için
    unique_values = [] # Sonuçları tutmak için liste
    for val, cp in zip(series, counterpart):
        new_val = val
        if new_val in seen:
            candidate = f"{new_val} ({cp})"
            counter = 1
            unique_candidate = candidate
            while unique_candidate in seen:
                counter += 1
                unique_candidate = f"{candidate} ({counter})"
            new_val = unique_candidate
        seen[new_val] = True
        unique_values.append(new_val)
    return unique_values

# Her iki sütun için benzersiz değerler oluşturuyoruz:
df.loc[:, "Job Titles_En"] = make_unique_with_counterpart(en_original, tr_original)
df.loc[:, "Turkce_Meslek"] = make_unique_with_counterpart(tr_original, en_original)

# --- Sonucu Kaydet ---
df.to_csv(output_file, index=False)
print(f"Benzersiz hale getirilmiş CSV '{output_file}' dosyası olarak kaydedildi.")
