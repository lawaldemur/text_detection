import os, time, sched, json, requests, datetime
from importlib import import_module
from shutil import copyfile
from flask import Flask, render_template, Response, request
from threading import Thread
from detect import detect


# local: for mac os 0.0.0.0:5001, for windows 127.0.0.1:30
ip, port = '0.0.0.0', 5001
app = Flask(__name__, static_url_path='', static_folder=os.getcwd() + '/images/')


@app.route('/')
def index():
    # Video streaming home page.
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process_img():
    file = request.files['image']
    path = os.path.join(os.getcwd() + '/images/', file.filename)
    file.save(path)

    return detect(path)


if __name__ == '__main__':
    app.run(host=ip, port=port, threaded=True)

