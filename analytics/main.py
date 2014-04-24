#! coding: utf-8


from rq import Queue
from redis import Redis
from datetime import timedelta
from flask import (Flask, jsonify, request,
                   render_template, url_for, redirect)

import api
import settings


app = Flask(__name__)
app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=60)



@app.route('/')
def home():
    time_info = api.get_time()

    return render_template('base.html', time_info=time_info)


@app.route('/compare')
def compare_info():
    url1 = request.args.get('url1')
    url2 = request.args.get('url2')
    if url1 and url2:
        url1 = url1.strip()
        url2 = url2.strip()
        webpage_info1 = api.get_webpage_info(url1)
        webpage_info2 = api.get_webpage_info(url2)
        overview_infos = []
        if webpage_info1 and webpage_info2:
            for webpage_info in [webpage_info1,webpage_info2]:
                overview_info = {
                    'pagespeed_score': webpage_info.get('pagespeed').get('score'),
                    'yslow_score': webpage_info.get('yslow').get('o'),
                    'pageload_time': '%0.2f' % (float(webpage_info.get('yslow').get('lt'))/1000),
                    'page_size': api.convert_size(float(webpage_info.get('yslow').get('w'))),
                    'total_request': webpage_info.get('yslow').get('r')
                }
                overview_infos.append(overview_info)

            return render_template('base.html', overview_infos=overview_infos)

        return redirect('/compare?url1=%s&url2=%s' % (url1, url2))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
