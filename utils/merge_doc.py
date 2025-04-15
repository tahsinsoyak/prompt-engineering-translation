import pandas as pd
import glob
import os
import re

# --- Dosya Yollarını Ayarla ---
folder_path = "docs_translated"   # CSV dosyalarınızın bulunduğu klasör
output_file = "merged_jobs.csv"   # Çıkış dosyası ismi

# --- Doğal (Numeric) Sıralama İçin Yardımcı Fonksiyon ---
def natural_key(string):
    """
    Dosya isimlerindeki sayıları integer olarak ayıklayarak,
    doğal sıralama yapılmasını sağlar.
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', string)]

# --- Klasördeki Tüm CSV Dosyalarını Bul ve Doğal Sıralama Yap ---
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
csv_files.sort(key=natural_key)

if not csv_files:
    print("Belirtilen klasörde CSV dosyası bulunamadı.")
else:
    merged_list = []  # Birleştirilecek DataFrame'leri tutmak için liste

    # İlk dosyayı normal (header ile) oku
    first_df = pd.read_csv(csv_files[0])
    merged_list.append(first_df)

    # İlk dosyanın sütun isimlerini al
    col_names = first_df.columns.tolist()

    # İlk dosya dışındaki diğer dosyalardan, başlık satırını atlayarak oku
    for csv_file in csv_files[1:]:
        df = pd.read_csv(csv_file, skiprows=1, header=None, names=col_names)
        merged_list.append(df)

    # Tüm DataFrame'leri birleştir (satır bazında)
    merged_df = pd.concat(merged_list, ignore_index=True)

    # Birleştirilmiş DataFrame'i CSV dosyası olarak kaydet
    merged_df.to_csv(output_file, index=False)
    print(f"Birleştirilmiş CSV başarıyla '{output_file}' dosyasına kaydedildi.")
