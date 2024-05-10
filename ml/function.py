import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge
from datetime import datetime

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

# Import API BMKG untuk wilayah Semarang
bmkg_api = pd.read_json('https://cuaca-gempa-rest-api.vercel.app/weather/jawa-tengah/semarang')

# Ambil tanggal dari BMKG 
tanggal = bmkg_api['data']['params'][0]['times'][0]['datetime']

# Hapus bagian tanggal dari BMKG
tanggal = tanggal[:-4]

# Ubah format menjadi datetime
tanggal = datetime.strptime(str(tanggal), '%Y%m%d')
tanggal = tanggal.date()

# Ambil humiditas dari BMKG
malem12 = bmkg_api['data']['params'][0]['times'][0]['value']
malem12 = malem12.replace("%", "")
pagi6 = bmkg_api['data']['params'][0]['times'][1]['value']
pagi6 = pagi6.replace("%", "")
siang12 = bmkg_api['data']['params'][0]['times'][2]['value']
siang12 = siang12.replace("%", "")
sore18 = bmkg_api['data']['params'][0]['times'][3]['value']
sore18 = sore18.replace("%", "")

# Hitung rata-rata humiditas dari BMKG
inRhavg = int((int(malem12)+int(pagi6)+int(siang12)+int(sore18))/4)

# Hitung rata-rata suhu
inTavg = bmkg_api['data']['params'][5]['times']
malem12 = inTavg[0]["celcius"]
malem12 = malem12.replace("C", "")
pagi6 = inTavg[1]["celcius"]
pagi6 = pagi6.replace("C", "")
siang12 = inTavg[2]["celcius"]
siang12 = siang12.replace("C", "")
sore18 = inTavg[3]["celcius"]
sore18 = sore18.replace("C", "")
inTavg = (int(malem12)+int(pagi6)+int(siang12)+int(sore18))/4
inTavg = round(inTavg)

# Ambil suhu maksimal dari BMKG
inTmax = bmkg_api['data']['params'][2]['times'][0]['celcius']
inTmax = inTmax.replace("C", "")
inTmax = int(inTmax)

# Ambil suhu minimal dari BMKG
inTmin = bmkg_api['data']['params'][4]['times'][0]['celcius']
inTmin = inTmin.replace("C", "")
inTmin = int(inTmin)

# Semua parameter dari BMKG diubah menjadi DataFrame untuk membuat prediksi hari ini
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

tavg_h = inTavg

print(tavg_h)

tavg_h1 = prediksi_besok['Tavg'].iloc[0]

print(tavg_h1)

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
predictions_5_days['Tn'] = predictions_5_days['Tn'].astype(int)
predictions_5_days['Tx'] = predictions_5_days['Tx'].astype(int)
predictions_5_days['Tavg'] = predictions_5_days['Tavg'].astype(int)
predictions_5_days['RH_avg'] = predictions_5_days['RH_avg'].astype(int)

# Menampilkan prediksi 5 hari ke depan
print(predictions_5_days)
