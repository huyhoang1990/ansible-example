#! coding: utf-8
__author__ = 'thanhdl'

"""
Nhớ cài phantomjs
"""

from flask import Flask, jsonify, request, render_template, url_for, redirect
import requests
from commands import getstatusoutput
import settings
import api

app = Flask(__name__)


@app.route('/')
def index():
    data = {
        'time': api.get_time(),
    }
    return render_template('base.html', **data)


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


@app.route('/compare_info', methods=['POST', 'GET'])
def compare_info():
    if request.method == 'POST':
        if request.form.get('compare-url'):
            url = request.form.get('compare-url')
            bg = 'http://api.thumbalizr.com/?url=%s&width=172' % url
            dict_info = {
                'bg': bg,
                'link': url,
                'time': api.get_time()
            }
            dict_summary = {
                'pagespeed_score': api.pagespeed(url)['score'],
                'yslow_score': api.yslow(url)['score']
            }
            info = render_template('compare_info.html', **dict_info)
            summary = render_template('compare_summary.html', **dict_summary)
            result = {
                'info': info,
                'summary': summary
            }
            return jsonify(result)
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
