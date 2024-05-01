from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from datetime import datetime

app = Flask(__name__)

df = pd.read_csv("dataset/cuaca_2017_2023.csv")
df['Tanggal'] = pd.to_datetime(df['Tanggal'])

data_pelatihan = df[df['Tanggal'].dt.year < 2024]

X = data_pelatihan[['Tn', 'Tx']].values
y = data_pelatihan['Tavg'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

tanggal_2024 = pd.date_range(start='2024-01-01', end='2024-12-31')

X_2024 = df[df['Tanggal'].dt.year == 2020][['Tn', 'Tx']].values
prediksi_suhu_2024 = model.predict(X_2024)

# Evaluasi performa menggunakan RMSE
#rmse = np.sqrt(mean_squared_error(y_test, y_predict))
#print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")

hasil_prediksi = pd.DataFrame({'Tanggal': tanggal_2024, 'Prediksi_Tavg': prediksi_suhu_2024})


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        tanggal_input = request.form['tanggal']
        try:
            tanggal = datetime.strptime(tanggal_input, '%Y-%m-%d')
            if tanggal.date() in hasil_prediksi['Tanggal'].dt.date.values:
                hasil = f'Prediksi suhu untuk tanggal {tanggal_input} adalah: {hasil_prediksi[hasil_prediksi["Tanggal"].dt.date == tanggal.date()]["Prediksi_Tavg"].values[0]:.2f}'
            else:
                hasil = f'Tanggal yang Anda masukkan: {tanggal.strftime("%d %B %Y")}'
        except ValueError:
            hasil = 'Format tanggal tidak valid'    
        return render_template('index.html', hasil=hasil)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

