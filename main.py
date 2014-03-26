#! coding: utf-8
__author__ = 'thanhdl'

"""
Nhớ cài phantomjs
"""

from flask import Flask, jsonify, request, render_template, url_for
import requests
from commands import getstatusoutput
import settings

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/pagespeed', methods=['POST', 'GET'])
def pagespeed():
    error = None
    if request.method == 'POST':
        url = request.form['url']
        if url:
            url = '%s%s' % (settings.API_URL, url)
            result = requests.get(url)
            if result:
                return jsonify(result.json())
            else:
                error = 'Invalid url'
                return render_template('error.html', error=error)
        else:
            error = 'Please enter a valid url'
            return render_template('error.html', error=error)
    else:
        return render_template('error.html', error=error)


@app.route('/yslow', methods=['POST', 'GET'])
def yslow():
    error = None
    if request.method == 'POST':
        url = request.form['url']
        if url:
            command = 'phantomjs %s --info all %s' % (settings.YSLOW_JS, url)
            print command
            status, output = getstatusoutput(command)
            if status == 0:
                return output
            else:
                return render_template('error.html', error=error)
        else:
            error = 'Invalid url'
            return render_template('error.html', error=error)
    else:
        return render_template('error.html', error=error)


if __name__ == '__main__':
    app.run(debug=True)
