from datetime import datetime, timedelta
import pytz

# Tentukan zona waktu Asia/Jakarta
indonesia = pytz.timezone('Asia/Jakarta')

# Ambil tanggal dan waktu saat ini dalam zona waktu yang ditentukan
sekarang = datetime.now(indonesia)

# Tambahkan satu hari untuk mendapatkan tanggal besok
besok = sekarang + timedelta(days=1)

# Tampilkan tanggal besok dalam format YYYY-MM-DD
tanggal_besok = besok.strftime('%Y-%m-%d')
print("Tanggal besok di zona waktu Asia/Jakarta:", tanggal_besok)

