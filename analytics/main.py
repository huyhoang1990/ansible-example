#! coding: utf-8


from rq import Queue
from redis import Redis
from datetime import timedelta
from flask import (Flask, jsonify, request, abort,
                   render_template, url_for, redirect)

import api
import time
import settings


app = Flask(__name__)
app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=60)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/powerup')
def test():
    return render_template('powerup.html')


@app.route('/compare_powerup', methods=['GET', 'POST'])
def compare_powerup():
    if request.method == 'POST':
        url1 = request.form.get('url1')
        url2 = request.form.get('url2')
        created_time = int(time.time())

    else:
        url1 = request.args.get('url1')
        url2 = request.args.get('url2')
        created_time = request.args.get('created_time')

    if url1 and url2:
        url1 = url1.strip()
        url2 = url2.strip()

        webpage_info1 = api.get_webpage_info(url1, created_time)
        webpage_info2 = api.get_webpage_info(url2, created_time)

        if webpage_info1 and webpage_info2:
            overview_info1 = {
                'pagespeed_score': webpage_info1.get('pagespeed').get('score'),
                'yslow_score': webpage_info1.get('yslow').get('yslow_score'),
                'pageload_time': webpage_info1.get('yslow').get('pageload_time'),
                'page_size': webpage_info1.get('yslow').get('page_size'),
                'total_request': webpage_info1.get('yslow').get('total_request')
            }

            overview_info2 = {
                'pagespeed_score': webpage_info2.get('pagespeed').get('score'),
                'yslow_score': webpage_info2.get('yslow').get('yslow_score'),
                'pageload_time': webpage_info2.get('yslow').get('pageload_time'),
                'page_size': webpage_info2.get('yslow').get('page_size'),
                'total_request': webpage_info2.get('yslow').get('total_request')
            }

            return render_template('overview.html',
                                   url1=url1, url2=url2,
                                   overview_info1=overview_info1,
                                   overview_info2=overview_info2)

        time.sleep(1)

        return redirect('/compare_powerup?url1=%s&url2=%s&created_time=%s' % \
                        (url1, url2, created_time))

    abort(400)


@app.route('/compare_directly', methods=['GET', 'POST'])
def compare_directly():
    if request.method == 'POST':
        url = request.form.get('url')
        created_time = int(time.time())

    else:
        url = request.args.get('url')
        created_time = request.args.get('created_time')

    if url:
        url = url.strip()
        webpage_info = api.get_webpage_info(url, created_time)
        if webpage_info:

            overview_info = {
                'pagespeed_score': webpage_info.get('pagespeed').get('score'),
                'yslow_score': webpage_info.get('yslow').get('yslow_score'),
                'pageload_time': webpage_info.get('yslow').get('pageload_time'),
                'page_size': webpage_info.get('yslow').get('page_size'),
                'total_request': webpage_info.get('yslow').get('total_request')
            }
            return render_template('overview.html', overview_info=overview_info)

        time.sleep(1)

        return redirect('/compare_directly?url=%s&created_time=%s' % \
                        (url, created_time))

    abort(400)


@app.route('/nginxpubsub', methods=['GET', 'POST'])
def nginxpubsub():
    return render_template('nginxpubsub.html')


@app.route('/homemaxcdn', methods=['GET', 'POST'])
def homecdn():
    return render_template('home_maxcdn_single.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
