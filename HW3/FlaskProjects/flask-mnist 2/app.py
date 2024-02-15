from flask import Flask, g, render_template, request

import sklearn as sk
import matplotlib.pyplot as plt
import numpy as np
import pickle
import os
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

import io
import base64

### stuff from last class
app = Flask(__name__)

@app.route('/')
def main():
    return render_template('main_better.html')

@app.route('/ask/', methods=['POST', 'GET'])
def ask():
    if request.method == 'GET':
        return render_template('ask.html')
    else:
        try:
            return render_template('ask.html', name=request.form['name'], student=request.form['student'])
        except:
            return render_template('ask.html')

@app.route('/hello/')
def hello():
    return render_template('hello.html')

@app.route('/hello/<name>')
def hello_name(name):
    return render_template('hello.html', name=name)

#######
# Request object: https://flask.palletsprojects.com/en/2.1.x/api/#flask.Request
@app.route('/submit-basic/', methods=['POST', 'GET'])
def submit_basic():
    if request.method == 'GET':
        return render_template('submit-basic.html')
    else:
        try:
            # this is how you can access the uploaded file
            # img = request.files['image']
            return render_template('submit-basic.html', thanks=True)
        except:
            return render_template('submit-basic.html', error=True)


# matplotlib: https://matplotlib.org/3.5.0/gallery/user_interfaces/web_application_server_sgskip.html
# plotly: https://towardsdatascience.com/web-visualization-with-plotly-and-flask-3660abf9c946
@app.route('/submit-advanced/', methods=['POST', 'GET'])
def submit():
    if request.method == 'GET':
        return render_template('submit.html')
    else:
        try:            
            '''
            1. Access the image
            2. Load the pickled ML model
            3. Run the ML model on the image
            4. Store the ML model's prediction in some Python variable
            5. Show the image on the template
            6. Print the prediction and some message on the template
            '''
            # 1
            img = request.files['image'] # file object 144.txt 
            img = np.loadtxt(img) # numpy array with the pixel values

            x = img.reshape(1, 64)
            
            # 2
            model = pickle.load(open('mnist-model/model.pkl', 'rb'))
            
            # 3, 4
            digit = model.predict(x)[0]

            # 5 
            fig = Figure(figsize=(3, 3))
            ax = fig.add_subplot(1, 1, 1,)
            ax.imshow(img, cmap='binary')
            ax.axis("off")

            # weird part of 5
            pngImage = io.BytesIO()
            FigureCanvas(fig).print_png(pngImage) # convert the pyplot figure object to a PNG image

            # encode the PNG image to base64 string
            pngImageB64String = "data:image/png;base64,"
            pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')

            return render_template('submit.html',
             image=pngImageB64String, digit=digit)
        except:
            return render_template('submit.html', error=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
