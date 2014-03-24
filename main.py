__author__ = 'thanhanpc'

from flask import Flask, jsonify, request, render_template, url_for
import requests
import settings

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ps', methods=['POST', 'GET'])
def pagespeedresult():
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


@app.route('/ys')
def yslowresult():
    return 'ok'

if __name__ == '__main__':
    app.run(debug=True)
