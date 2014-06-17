#! coding: utf-8


from rq import Queue
from redis import Redis
from urlparse import urlparse
from datetime import timedelta
from simplejson import dumps, loads
from flask import (Flask, jsonify, request, abort,
                   render_template, make_response, redirect, send_from_directory)

import api
import time
import settings


app = Flask(__name__)
app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=60)


@app.route('/', methods=['GET', 'POST'])
def home():

    scores = {
        'Page Speed Grade': 'pagespeed_score',
        'Yslow Grade': 'yslow_score',
        'Total Page Size': 'page_size',
        'Total # of requests': 'total_request'
    }

    if request.method == 'GET':

        return render_template('home.html',
                               status='Ready',
                               scores=scores,
                               locations=settings.LOCATIONS)

    else:
        url = request.form.get('url')
        is_slaver = None

        # Xử lý trường hợp request post từ master tới slave
        if not url:
            called_from = request.args.get('called_from')
            if called_from:
                is_slaver = True
                created_time = request.args.get('created_time')
                channel_id = request.args.get('channel_id')
                url = request.args.get('url')

                api.get_webpage_info(url, created_time,
                                     channel_id, is_slaver)

                return 'OK'

        if url:
            url = url.strip()
            is_webpage = api.is_webpage(url)
            if is_webpage is None:
                abort(400)

            if is_webpage is False:
                scores = {}

            channel_id = str(time.time())
            created_time = int(time.time())

            api.get_webpage_info(url, created_time,
                                 channel_id, is_slaver)

            slaver_servers = api.get_slaver_servers()
            locations = settings.LOCATIONS

            master_location_id = None

            for server in locations:
                if locations[server]['host'] == settings.MASTER_SERVER:
                    master_location_id = locations[server]['id']

            return render_template('result_one_page.html',
                                   status='Checking....',
                                   locations=settings.LOCATIONS,
                                   scores=scores,
                                   channel_id=channel_id,
                                   is_webpage=is_webpage,
                                   master_location_id=master_location_id,
                                   master_server=settings.MASTER_SERVER,
                                   slaver_servers=dumps(slaver_servers))

        abort(400)


@app.route('/powerup', methods=['GET', 'POST'])
def compare_powerup():
    scores = {
        'Page Speed Grade': 'pagespeed_score',
        'Yslow Grade': 'yslow_score',
        'Total Page Size': 'page_size',
        'Total # of requests': 'total_request'
    }

    if request.method == 'GET':
        domain = request.args.get('domain')
        temporary_domain = request.args.get('domain_demo')
        if domain and temporary_domain:
            api.set_temporary_url(domain, temporary_domain)

        render_powerup = True
        return render_template('home.html',
                               render_powerup=render_powerup,
                               status='Ready',
                               scores=scores,
                               locations=settings.LOCATIONS,
                               domain=domain,
                               temporary_domain=temporary_domain)

    else:
        powerup_url = request.form.get('powerup_url')
        is_slaver = None

        # Xử lý trường hợp request post từ master tới slave
        if not powerup_url:
            called_from = request.args.get('called_from')
            if called_from:
                is_slaver = True
                created_time = request.args.get('created_time')
                channel_id = request.args.get('channel_id')
                powerup_url = request.args.get('url')
                temporary_url = api.get_temporary_url(powerup_url)
                api.get_webpage_info(powerup_url, created_time,
                                     channel_id, is_slaver,
                                     is_powerup_domain=True)

                api.get_webpage_info(temporary_url, created_time,
                                     channel_id, is_slaver,
                                     is_powerup_domain=False)

                return 'OK'

        if powerup_url:
            powerup_url = powerup_url.strip()

            temporary_url = api.get_temporary_url(powerup_url)

            channel_id = str(time.time())
            created_time = int(time.time())

            slaver_servers = api.get_slaver_servers()
            locations = settings.LOCATIONS

            master_location_id = None

            for server in locations:
                if locations[server]['host'] == settings.MASTER_SERVER:
                    master_location_id = locations[server]['id']

            # api.get_webpage_info(powerup_url, created_time,
            #                      channel_id, is_slaver,
            #                      is_powerup_domain=True)
            #
            # api.get_webpage_info(temporary_url, created_time,
            #                      channel_id, is_slaver,
            #                      is_powerup_domain=False)


            api.CREATE_WEBPAGE_QUEUE.enqueue(api.get_video_filmstrip, powerup_url,
                                             temporary_url, created_time, channel_id)

            # video_path = '/srv/loadreport/filmstrip/%s_%s' % \
            #              (channel_id, urlparse(powerup_url).netloc)
            #
            # video_path = '/srv/loadreport/filmstrip/1402890008.17_kenh14.vn'
            #
            #
            # return render_template('video.html',
            #                        channel_id=channel_id,
            #                        domain=powerup_url)

            return render_template('result_powerup.html',
                                   status='Checking...',
                                   locations=settings.LOCATIONS,
                                   scores=scores,
                                   channel_id=channel_id,
                                   slaver_servers=slaver_servers,
                                   master_server=settings.MASTER_SERVER,
                                   master_location_id=master_location_id)


        abort(400)


@app.route('/video')
def video():
    channel_id = request.args.get('channel_id')
    domain = request.args.get('domain')
    domain = urlparse(domain).netloc
    path = '/srv/loadreport/filmstrip/%s_%s' % (channel_id, domain)
    return send_from_directory(path, 'out_merge.mp4')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
