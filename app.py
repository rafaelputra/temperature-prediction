from flask import Flask, render_template, request
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from ml.function import *

app = Flask(__name__)

mapping_hari = {
    'Monday': 'Senin',
    'Tuesday': 'Selasa',
    'Wednesday': 'Rabu',
    'Thursday': 'Kamis',
    'Friday': 'Jumat',
    'Saturday': 'Sabtu',
    'Sunday': 'Minggu'
}

@app.route('/', methods=['GET', 'POST'])
def main():
    indonesia = pytz.timezone('Asia/Jakarta')
    # Dapatkan tanggal dan waktu sekarang dalam zona waktu Indonesia
    sekarang = datetime.now(indonesia)
    # Buat list untuk menyimpan data hari dan tanggal untuk 7 hari ke depan
    data_hari = []
    for i in range(7):
        # Hitung tanggal untuk hari ke-i dari sekarang
        hari = sekarang + timedelta(days=i)
        # Dapatkan nama hari dalam Bahasa Indonesia menggunakan pemetaan
        nama_hari = mapping_hari[hari.strftime("%A")]
        # Format tanggal menjadi DD-MM-YYYY
        tanggal = hari.strftime("%d-%m-%Y")
        # Tambahkan data hari ke list
        data_hari.append({'nama_hari': nama_hari, 'tanggal': tanggal})

    # Setiap hari memiliki variabel tanggal yang berbeda
    hari_h = data_hari[0]['nama_hari']
    hari_h1 = data_hari[1]['nama_hari']
    hari_h2 = data_hari[2]['nama_hari']
    hari_h3 = data_hari[3]['nama_hari']
    hari_h4= data_hari[4]['nama_hari']
    hari_h5 = data_hari[5]['nama_hari']
    hari_h6 = data_hari[6]['nama_hari']
    tanggal_h = data_hari[0]['tanggal']
    tanggal_h1 = data_hari[1]['tanggal']
    tanggal_h2 = data_hari[2]['tanggal']
    tanggal_h3 = data_hari[3]['tanggal']
    tanggal_h4 = data_hari[4]['tanggal']
    tanggal_h5 = data_hari[5]['tanggal']
    tanggal_h6 = data_hari[6]['tanggal']

    # Render template HTML dan kirimkan data hari
    tavgh = inTavg
    tavgh1 = prediksi_besok['Tavg'].iloc[0]
    return render_template('index.html', 
                           hari_h=hari_h,
                           hari_h1=hari_h1,
                           hari_h2=hari_h2,
                           hari_h3=hari_h3,
                           hari_h4=hari_h4,
                           hari_h5=hari_h5,
                           hari_h6=hari_h6,
                           tanggal_h=tanggal_h,
                           tanggal_h1=tanggal_h1,
                           tanggal_h2=tanggal_h2,
                           tanggal_h3=tanggal_h3,
                           tanggal_h4=tanggal_h4,
                           tanggal_h5=tanggal_h5,
                           tanggal_h6=tanggal_h6,
                           tavg_h=tavgh,
                           tavg_h1=tavgh1)

@app.route('/about')
def about():
    return render_template('about.html')
    
@app.route('/playground')
def playground():
    return render_template('playground.html')

if __name__ == '__main__':
    app.run(debug=True, port=6969)
