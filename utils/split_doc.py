import pandas as pd
import math

# --- Adım 1: Dosyayı Oku ---
# jobs.xlsx dosyasını oku.
df = pd.read_excel("jobs.xlsx")

# --- Adım 2: Parça Boyutunu Belirle ---
chunk_size = 500  # Her bir dosyada 500 satır bulunacak

# --- Adım 3: Toplam Parça Sayısını Hesapla ---
nrows = df.shape[0]
n_chunks = math.ceil(nrows / chunk_size)

# --- Adım 4: Verileri Parçalara Böl ve Her Birini Ayrı Excel Dosyası Olarak Kaydet ---
for i in range(n_chunks):
    start_index = i * chunk_size
    end_index = start_index + chunk_size
    # Parça DataFrame'ini oluştur
    chunk_df = df.iloc[start_index:end_index]
    
    # Dosya adını oluştur
    output_filename = f"docs/jobs_part_{i+1}.xlsx"
    # Parçayı Excel dosyası olarak kaydet (index sütununu dahil etmiyoruz)
    chunk_df.to_excel(output_filename, index=False)
    print(f"{output_filename} dosyası başarıyla kaydedildi.")
