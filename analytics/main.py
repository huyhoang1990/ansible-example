#! coding: utf-8


from flask import Flask, jsonify, request, render_template, url_for, redirect
import api
from redis import Redis
from rq import Queue
import time
import settings

redis_conn = Redis()
pagespeed_queue = Queue(connection=redis_conn, default_timeout=3600)
yslow_queue = Queue(connection=redis_conn, default_timeout=3600)
har_queue = Queue(connection=redis_conn, default_timeout=3600)

app = Flask(__name__)


@app.route('/')
def index():
    data = {
        'time': api.get_time(),
    }
    return render_template('base.html', **data)


@app.route('/compare_info', methods=['POST', 'GET'])
def compare_info():
    if request.method == 'POST':
        if request.form.get('compare-url'):
            url = request.form.get('compare-url')

            r_pagespeed = pagespeed_queue.enqueue(api.pagespeed, url)
            r_yslow = yslow_queue.enqueue(api.yslow, url)
            r_har = har_queue.enqueue(api.generate_har_file, url)
            time.sleep(8)

            bg = 'http://api.thumbalizr.com/?url=%s&width=172' % url

            dict_info = {
                'bg': bg,
                'link': url,
                'time': api.get_time()
            }

            dict_summary = {
                'pagespeed_score': r_pagespeed.result['score'],
                'yslow_score': r_yslow.result['o'],
                'pageload_time': '%0.2f' % (float(r_yslow.result['lt'])/1000),
                'page_size': api.convert_size(float(r_yslow.result['w'])),
                'total_request': r_yslow.result['r']
            }

            title_yslow = []
            for key in r_yslow.result['g']:
                title_yslow.append(key)

            dict_yslow = []
            for i in title_yslow:
                if 'score' in r_yslow.result['g'][i]:
                    dict_yslow.append(r_yslow.result['g'][i]['score'])
                else:
                    dict_yslow.append('n/a')

            title_pagespeed = []
            for key in r_pagespeed.result['formattedResults']['ruleResults']:
                title_pagespeed.append(key)

            dict_pagespeed = []
            for i in title_pagespeed:
                if 'ruleImpact' in r_pagespeed.result['formattedResults']['ruleResults'][i]:
                    data = (1 - r_pagespeed.result['formattedResults']['ruleResults'][i]['ruleImpact'])*100
                    if data < 0:
                        dict_pagespeed.append('n/a')
                    else:
                        dict_pagespeed.append(int(data))
                else:
                    dict_pagespeed.append('n/a')

            directory_har_file = settings.HAR_SERVER + r_har.result

            info = render_template('compare_info.html', **dict_info)
            summary = render_template('compare_summary.html', **dict_summary)
            result_yslow = render_template('yslow_results.html', dict_yslow=dict_yslow)
            result_pagespeed = render_template('pagespeed_results.html', dict_pagespeed=dict_pagespeed)
            result_har = render_template('har_results.html', directory_har_file=directory_har_file)
            result = {
                'info': info,
                'summary': summary,
                'result_yslow': result_yslow,
                'result_pagespeed': result_pagespeed,
                'result_har': result_har
            }
            return jsonify(result)
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
