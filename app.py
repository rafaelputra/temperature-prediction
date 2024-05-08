from flask import Flask, render_template, request
import pandas as pd
import numpy as np
from ml.function import *

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def main():
    tn_value = prediksi_besok['Tn'].iloc[0]
    return render_template('index.html', tn=tn_value)

@app.route('/about')
def about():
    return render_template('about.html')
    
@app.route('/playground')
def playground():
    return render_template('playground.html')

if __name__ == '__main__':
    app.run(debug=True, port=6969)

