# Import library
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge
from datetime import datetime, date
import firebase_admin
from firebase_admin import db, credentials

# Import dataset serta mengatur index pada kolom Tanggal
df = pd.read_csv('https://drive.google.com/uc?export=view&id=1SbNCFBEHhLQHEzXlpAlRYhBOjwvcUNKi',index_col='Tanggal')

# Mengubah tipe data kolom Tanggal menjadi datetime
df.index=pd.to_datetime(df.index)

# Parameter yang akan digunakan
parameter = df[['Tn', 'Tx', 'Tavg', 'RH_avg']].copy()

# Menggunakan fungsi Ridge Regression pada sklearn untuk masing-masing 
tn = Ridge(alpha=.1)
tx = Ridge(alpha=.1)
tavg = Ridge(alpha=.1)
rhavg = Ridge(alpha=.1)

# Menggeser nilai Tn ke belakang
parameter['ttn']=parameter.shift(-1)['Tn']

# Menggeser nilai Tx ke belakang
parameter['ttx']=parameter.shift(-1)['Tx']

# Menggeser nilai Tavg ke belakang
parameter['ttavg']=parameter.shift(-1)['Tavg']

# Menggeser nilai RH_avg ke belakang
parameter['ttrh']=parameter.shift(-1)['RH_avg']

# Mengisi nilai kolom yang kosong setelah digeser
parameter = parameter.ffill()

# Membuat predictor dari semua kolom kecuali target
predictors = parameter.columns[~parameter.columns.isin(['ttn' , 'ttx', 	'ttavg',	'ttrh'])]

# Membuat fungsi training dan testing untuk memprediksi Tn
def backtesttn(parameter, model, predictors, start=365*6, step=90):
  all_predictions = []

  for i in range(start, parameter.shape[0], step):
    train = parameter.iloc[:i,:]
    test = parameter.iloc[i:(i+step),:]

    model.fit(train[predictors], train['ttn'])

    preds = model.predict(test[predictors])

    preds = pd.Series(preds, index = test.index)

    combined = pd.concat([test['ttn'], preds], axis=1)
    combined.columns = ["aktual","prediksi"]

    combined["diff"]= (combined['prediksi'] - combined['aktual']).abs()
    all_predictions.append(combined)
  return pd.concat(all_predictions)

# Membuat fungsi training dan testing untuk memprediksi Tx
def backtesttx(parameter, model, predictors, start=365*6, step=90):
  all_predictions = []

  for i in range(start, parameter.shape[0], step):
    train = parameter.iloc[:i,:]
    test = parameter.iloc[i:(i+step),:]

    model.fit(train[predictors], train['ttx'])

    preds = model.predict(test[predictors])

    preds = pd.Series(preds, index = test.index)

    combined = pd.concat([test['ttx'], preds], axis=1)
    combined.columns = ["aktual","prediksi"]

    combined["diff"]= (combined['prediksi'] - combined['aktual']).abs()
    all_predictions.append(combined)
  return pd.concat(all_predictions)

# Membuat fungsi training dan testing untuk memprediksi Tavg
def backtesttavg(parameter, model, predictors, start=365*6, step=90):
  all_predictions = []


  for i in range(start, parameter.shape[0], step):
    train = parameter.iloc[:i,:]
    test = parameter.iloc[i:(i+step),:]

    model.fit(train[predictors], train['ttavg'])

    preds = model.predict(test[predictors])

    preds = pd.Series(preds, index = test.index)

    combined = pd.concat([test['ttavg'], preds], axis=1)
    combined.columns = ["aktual","prediksi"]

    combined["diff"]= (combined['prediksi'] - combined['aktual']).abs()
    all_predictions.append(combined)
  return pd.concat(all_predictions)

# Membuat fungsi training dan testing untuk memprediksi RH
def backtestrh(parameter, model, predictors, start=365*6, step=90):
  all_predictions = []


  for i in range(start, parameter.shape[0], step):
    train = parameter.iloc[:i,:]
    test = parameter.iloc[i:(i+step),:]

    model.fit(train[predictors], train['ttrh'])

    preds = model.predict(test[predictors])

    preds = pd.Series(preds, index = test.index)

    combined = pd.concat([test['ttrh'], preds], axis=1)
    combined.columns = ["aktual","prediksi"]
    #membuat kolom diff
    combined["diff"]= (combined['prediksi'] - combined['aktual']).abs()
    all_predictions.append(combined)
  return pd.concat(all_predictions)

# Menggunakan fungsi backtest untuk masing-masing parameter
minimum = backtesttn(parameter, tn, predictors)
maksimum = backtesttx(parameter, tx, predictors)
rata = backtesttavg(parameter, tavg, predictors)
humiditas = backtestrh(parameter, rhavg, predictors)

# Mengautentikasi firebase
cred = credentials.Certificate("temprh-36591-firebase-adminsdk-6qoor-9ae6252178.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://temprh-36591-default-rtdb.asia-southeast1.firebasedatabase.app/"})

# Mengambil data dari firebase
intmin = db.reference('/DHT_11/Stats/TempMin')
inTmin = intmin.get()
intmax = db.reference('/DHT_11/Stats/TempMax')
inTmax = intmax.get()
intavg = db.reference('/DHT_11/Stats/TempAverage')
inTavg = intavg.get()
inrhavg = db.reference('/DHT_11/Stats/HumAverage')
inRhavg = inrhavg.get()
tanggal = date.today()

# Semua parameter dari firabase diubah menjadi DataFrame untuk membuat prediksi hari ini
predictor_hari_ini = pd.DataFrame({'date': [tanggal],
                                   'tmin': [inTmin],
                                   'tmax': [inTmax],
                                   'tavg': [inTavg],
                                   'rhavg': [inRhavg]
                                   })

# Memasukkan prediksi hari ini ke dalam fungsi Ridge Regression                                   
rn = pd.DataFrame([[inTmin, inTmax, inTavg, inRhavg]], columns=['Tn', 'Tx', 'Tavg', 'RH_avg'])
predtn = tn.predict(rn)
predtx = tx.predict(rn)
predtavg = tavg.predict(rn)
predrhavg = rhavg.predict(rn)

# Mengubah format agar menjadi bilangan integer
predtn = int(round(predtn.item()))
predtx = int(round(predtx.item()))
predtavg = int(round(predtavg.item()))
predrhavg = int(round(predrhavg.item()))

# Membuat DataFrame baru untuk menampung nilai prediksi besok
prediksi_besok = pd.DataFrame([[tanggal, predtn, predtx, predtavg, predrhavg]], columns=['tanggal', 'Tn', 'Tx', 'Tavg', 'RH_avg'])

#menampilkan prediksi besok
tavg_h1 = prediksi_besok['Tavg'].iloc[0]

# Menginisialisasi DataFrame untuk menyimpan prediksi 5 hari ke depan
predictions_5_days = pd.DataFrame(columns=['Tn', 'Tx', 'Tavg', 'RH_avg'])

# Menggunakan prediksi besok sebagai input untuk prediksi hari-hari berikutnya
rn = prediksi_besok[['Tn', 'Tx', 'Tavg', 'RH_avg']].copy()

for _ in range(5):
    # Memprediksi variabel suhu minimum, maksimum, rata-rata, dan rata-rata kelembaban
    predtn = tn.predict(rn[['Tn', 'Tx', 'Tavg', 'RH_avg']])[0]
    predtx = tx.predict(rn[['Tn', 'Tx', 'Tavg', 'RH_avg']])[0]
    predtavg = tavg.predict(rn[['Tn', 'Tx', 'Tavg', 'RH_avg']])[0]
    predrhavg = rhavg.predict(rn[['Tn', 'Tx', 'Tavg', 'RH_avg']])[0]

    # Menambahkan prediksi hari berikutnya ke dalam DataFrame
    new_prediction = pd.DataFrame({
                                   'Tn': [predtn],
                                   'Tx': [predtx],
                                   'Tavg': [predtavg],
                                   'RH_avg': [predrhavg]})
    
    # Memperbarui nilai rn untuk prediksi berikutnya
    rn = new_prediction.copy()
    
    # Menambahkan prediksi ke DataFrame prediksi_5_hari jika sudah tidak kosong
    if not predictions_5_days.empty:
        predictions_5_days = pd.concat([predictions_5_days, new_prediction], ignore_index=True)
    else:
        predictions_5_days = new_prediction.copy()

# Mengonversi nilai suhu menjadi integer
predictions_5_days['Tn'] = predictions_5_days['Tn'].round()
predictions_5_days['Tx'] = predictions_5_days['Tx'].round()
predictions_5_days['Tavg'] = predictions_5_days['Tavg'].round(1)
predictions_5_days['RH_avg'] = predictions_5_days['RH_avg'].round(1)