from flask import Flask, render_template, request
import pandas as pd
import numpy as np
from ml.function import *

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def main():
    tavg_h = rn['Tavg'].iloc[0].round().astype(int)
    tavg_h1 = prediksi_besok['Tavg'].iloc[0]
    tavg_h2 = predictions['Tavg'].iloc[0]
    tavg_h3 = predictions['Tavg'].iloc[1]
    tavg_h4 = predictions['Tavg'].iloc[2]
    tavg_h5 = predictions['Tavg'].iloc[3]
    tavg_h6 = predictions['Tavg'].iloc[4]
    return render_template('index.html', tavg_h=tavg_h, tavg_h1=tavg_h1, tavg_h2=tavg_h2, tavg_h3=tavg_h3, tavg_h4=tavg_h4, tavg_h5=tavg_h5, tavg_h6=tavg_h6)

@app.route('/about')
def about():
    return render_template('about.html')
    
@app.route('/playground')
def playground():
    return render_template('playground.html')

if __name__ == '__main__':
    app.run(debug=True, port=6969)

