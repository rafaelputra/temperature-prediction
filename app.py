# Import library
from flask import Flask, render_template, request
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from ml.function import *

# Inisialisasi Flask
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

# Mengubah zona waktu Indonesia
indonesia = pytz.timezone('Asia/Jakarta')
sekarang = datetime.now(indonesia)

@app.route('/', methods=['GET', 'POST'])
def main():
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

    # Mengambil nilai suhu rata-rata dari function
    tavgh = int(round(inTavg,0))
    tavgh1 = prediksi_besok['Tavg'].iloc[0]
    tavgh2 = predictions_5_days['Tavg'].iloc[0]
    tavgh3 = predictions_5_days['Tavg'].iloc[1]
    tavgh4 = predictions_5_days['Tavg'].iloc[2]
    tavgh5 = predictions_5_days['Tavg'].iloc[3]
    tavgh6 = predictions_5_days['Tavg'].iloc[4]

    # Mengambil nilai suhu minimum dari function
    tmin_h = int(round(inTmin,0))
    tminh1 = prediksi_besok['Tn'].iloc[0]
    tminh2 = predictions_5_days['Tn'].iloc[0]
    tminh3 = predictions_5_days['Tn'].iloc[1]
    tminh4 = predictions_5_days['Tn'].iloc[2]
    tminh5 = predictions_5_days['Tn'].iloc[3]
    tminh6 = predictions_5_days['Tn'].iloc[4]

    # Mengambil nilai suhu maksimal dari function
    tmax_h = int(round(inTmax,0))
    tmaxh1 = prediksi_besok['Tx'].iloc[0]
    tmaxh2 = predictions_5_days['Tx'].iloc[0]
    tmaxh3 = predictions_5_days['Tx'].iloc[1]
    tmaxh4 = predictions_5_days['Tx'].iloc[2]
    tmaxh5 = predictions_5_days['Tx'].iloc[3]
    tmaxh6 = predictions_5_days['Tx'].iloc[4]
    

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
                           tavg_h1=tavgh1,
                           tavg_h2=tavgh2,
                           tavg_h3=tavgh3,  
                           tavg_h4=tavgh4,
                           tavg_h5=tavgh5,
                           tavg_h6=tavgh6,
                           tmin_h=tmin_h,
                           tmin_h1=tminh1,
                           tmin_h2=tminh2,
                           tmin_h3=tminh3,
                           tmin_h4=tminh4,
                           tmin_h5=tminh5,
                           tmin_h6=tminh6,
                           tmax_h=tmax_h,
                           tmax_h1=tmaxh1,
                           tmax_h2=tmaxh2,
                           tmax_h3=tmaxh3,
                           tmax_h4=tmaxh4,
                           tmax_h5=tmaxh5,
                           tmax_h6=tmaxh6,)


@app.route('/about')
def about():
    return render_template('about.html')
    
@app.route('/playground', methods=['GET', 'POST'])
def playground():
    if request.method == 'POST':
        suhu_min = int(request.form['suhu_min'])
        suhu_max = int(request.form['suhu_max'])
        suhu_avg = int(request.form['suhu_avg'])
        kelembapan = int(request.form['kelembapan'])
        plygrnd = pd.DataFrame([[suhu_min, suhu_max, suhu_avg, kelembapan]], columns=['Tn', 'Tx', 'Tavg', 'RH_avg'])
        pptn = int(tn.predict(plygrnd).round())
        pptx = int(tx.predict(plygrnd).round())
        pptavg = int(tavg.predict(plygrnd).round())
        pprhavg = int(rhavg.predict(plygrnd).round())

        return render_template('playground.html',tavg_out = pptavg, tx_out = pptx, tn_out = pptn)
    else:
        return render_template('playground.html')

if __name__ == '__main__':
    app.run(debug=True, port=6969)
