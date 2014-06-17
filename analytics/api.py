#! coding: utf-8


from rq import Queue
from redis import Redis
from datetime import datetime
from urlparse import urlparse
from simplejson import dumps, loads
from commands import getstatusoutput
from pymongo import MongoClient as MongoDB

import os
import math
import urllib
import requests
import settings
import commands
import xmltodict

DATABASE = MongoDB(settings.MONGOD_SERVERS)[settings.DATABASE_NAME]
ANALYTICS = DATABASE.analytics
DOMAIN = DATABASE.domain

host, port, db = settings.REDIS_ANALYTICS_QUEUE.split(':')
TASK_QUEUE = Redis(host=host, port=int(port), db=int(db))
CREATE_WEBPAGE_QUEUE = Queue('crawl_webpage',
                             connection=TASK_QUEUE,
                             default_timeout=600)


def parse_pagespeed_info(pagespeed_info):
    if pagespeed_info.has_key('error'):
        return {'pagespeed_score': 'None'}

    pagespeed_details = pagespeed_info.get('formattedResults') \
                                      .get('ruleResults')

    result = {}
    result['pagespeed_score'] = pagespeed_info.get('score')

    for key in pagespeed_details:
        data = pagespeed_details.get(key).get('ruleImpact')
        if data is not None:
            data = (1 - data) * 100 if 1 > data else 'n/a'
            result[key] = data

        else:
            result[key] = 'n/a'

    return result


def get_pagespeed_info(url, created_time, channel_id, is_powerup_domain=None):
    if url:
        pagespeed_url = '%s%s' % (settings.PAGESPEED_URL, url)

        headers = {'Accept-Encoding': 'identity, deflate, compress, gzip',
                   'Accept': '*/*'}
        pagespeed_info = requests.get(pagespeed_url, headers=headers).json()
        if pagespeed_info:
            pagespeed_info = parse_pagespeed_info(pagespeed_info)

            if is_powerup_domain is not None:
                pagespeed_info['is_powerup_domain'] = is_powerup_domain

            push_to_browser(channel_id, pagespeed_info)

            if pagespeed_info:
                webpage_info = ANALYTICS.find_one({'url': url,
                                                   'created_time': created_time})
                if webpage_info:
                    ANALYTICS.update({'url': url,
                                      'created_time': created_time},
                                     {'$set': {'pagespeed': pagespeed_info}})

                else:
                    ANALYTICS.insert({'url': url,
                                      'created_time': created_time,
                                      'pagespeed': pagespeed_info})

                return True

    return False


def parse_yslow_info(yslow_info):
    result = {}
    result['pageload_time'] = '%s s' % str(float(yslow_info.get('lt'))/1000)
    result['page_size'] = convert_size(float(yslow_info.get('w')))
    result['total_request'] = yslow_info.get('r')
    result['yslow_score'] = yslow_info.get('o')

    yslow_details = yslow_info.get('g')
    for detail in yslow_details:
        if yslow_details[detail].has_key('score'):
            result[detail] = yslow_details[detail].get('score')
        else:
            result[detail] = 'n/a'

    return result


def get_yslow_info(url, created_time, channel_id,
                   is_slaver, is_powerup_domain=None):
    if url:
        command = 'phantomjs %s --info all --format xml %s' % (settings.YSLOW_JS, url)
        print command
        status, output = getstatusoutput(command)

        if status == 0:
            try:
                yslow_info = xmltodict.parse(output).get('results')
            except:
                yslow_info = {'pageload_time': 'None',
                              'page_size': 'None',
                              'total_request': 'None',
                              'yslow_score': 'None',
                              'is_powerup_domain': is_powerup_domain}

                push_to_browser(channel_id, yslow_info, is_slaver)
                return False

            if yslow_info:
                yslow_info = parse_yslow_info(yslow_info)
                if is_slaver:
                    yslow_info['is_slaver'] = True

                if is_powerup_domain is not None:
                    yslow_info['is_powerup_domain'] = is_powerup_domain

                push_to_browser(channel_id, yslow_info, is_slaver)

                if yslow_info:
                    webpage_info = ANALYTICS.find_one({'url': url,
                                                       'created_time': created_time})
                    if webpage_info:
                        ANALYTICS.update({'url': url,
                                          'created_time': created_time},
                                         {'$set': {'yslow': yslow_info}})

                    else:
                        ANALYTICS.insert({'url': url,
                                          'created_time': created_time,
                                          'yslow': yslow_info})

                return True

    return False


def get_harfile_info(url, created_time, channel_id):
    if url:
        time_now = datetime.now().strftime('%Y-%m-%d+%H:%M:%S')
        host = urlparse(url).netloc
        filename = '%s+%s%s' % (host, time_now, '.com.har')
        dir = '%s%s' % (settings.HARSTORE, filename)

        command = 'phantomjs %s %s > %s' % (settings.NETSNIFF, url, dir)
        status, output = getstatusoutput(command)
        if status == 0:
            source_file = 'file/%s' % filename
            webpage_info = ANALYTICS.find_one({'url': url,
                                               'created_time': created_time})
            if webpage_info:
                ANALYTICS.update({'url': url,
                                  'created_time': created_time},
                                 {'$set': {'harfile': source_file}})

            else:
                ANALYTICS.insert({'url': url,
                                  'created_time': created_time,
                                  'harfile': source_file})

            return True

    return False


def get_webpage_info(url, created_time, channel_id,
                     is_slaver, is_powerup_domain=None):

    created_time = int(created_time)
    webpage_info = ANALYTICS.find_one({'url': url,
                                       'created_time': created_time})


    if not webpage_info:
        ANALYTICS.insert({'url': url,
                          'created_time': created_time})

        CREATE_WEBPAGE_QUEUE.enqueue(get_yslow_info, url,
                                     created_time, channel_id,
                                     is_slaver, is_powerup_domain=is_powerup_domain)

        if not is_slaver:
            CREATE_WEBPAGE_QUEUE.enqueue(get_pagespeed_info, url,
                                        created_time, channel_id,
                                        is_powerup_domain=is_powerup_domain)

            # CREATE_WEBPAGE_QUEUE.enqueue(get_harfile_info, url,
            #                              created_time, channel_id)

            CREATE_WEBPAGE_QUEUE.enqueue(post_to_slaver_server, url,
                                         created_time, channel_id,
                                         is_powerup_domain=is_powerup_domain)

        return False


def get_video_filmstrip(powerup_url, temporary_url, created_time, channel_id):
    # import time
    # time.sleep(5)
    # data = {'video_path': 'http://10.2.14.22/video?channel_id=1403002928.33&domain=http://google.com'}
    #
    # push_to_browser(channel_id, data)
    # return True

    for url in [powerup_url, temporary_url]:
        host = urlparse(url).netloc
        if url == temporary_url:
            host = '%s_' % host

        command = 'cd %s ;sudo phantomjs loadreport.js %s filmstrip %s_%s' % \
                  (settings.LOADREPORT, url, channel_id, host)

        print command
        status, output = getstatusoutput(command)

        if status == 0:
            command = 'cd %s; sudo python convert.py %s/filmstrip/%s_%s/' % \
                      (settings.LOADREPORT, settings.LOADREPORT,
                       channel_id, host)

            status, output = getstatusoutput(command)
            if status == 0:
                command = 'cd %s/filmstrip/%s_%s; ' \
                          'sudo ffmpeg -i concat.txt -c:v libx264 -pix_fmt yuv420p out.mp4' % \
                          (settings.LOADREPORT, channel_id, host)

                print command
                status, output = getstatusoutput(command)
                print 'perfect'

    command = "cd %s/filmstrip/%s_%s ;" \
              "sudo ffmpeg -i out.mp4 -vf 'pad=2*iw:ih [left]; movie=%s/filmstrip/%s_%s_/out.mp4 [right];[left][right] overlay=main_w/2:0' out_merge.mp4" % \
              (settings.LOADREPORT, channel_id, urlparse(powerup_url).netloc,
               settings.LOADREPORT, channel_id, urlparse(temporary_url).netloc)

    print command

    status, output = getstatusoutput(command)
    if status == 0:
        path = 'http://%s/video?channel_id=%s&domain=%s' % \
               (settings.MASTER_SERVER, channel_id, powerup_url)
        data = {'video_path': path}

        push_to_browser(channel_id, data)
        return True

    return False


def convert_size(size):
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    if i == 1:
        s = int(size/p)
    else:
        s = round(size/p, 2)
    if s > 0:
        return '%s %s' % (s, size_name[i])
    else:
        return '0B'


def push_to_browser(channel_id, data, is_slaver=None):
    if is_slaver:
        cmd = "curl -s -v -X POST 'http://%s/pub?id=%s' -d '%s'" % \
                (settings.MASTER_SERVER, channel_id, dumps(data))

    else:
        cmd = "curl -s -v -X POST 'http://localhost/pub?id=%s' -d '%s'" % \
                (channel_id, dumps(data))
    print cmd

    os.system(cmd)

    return True


def is_webpage(url):
    try:
        info = urllib.urlopen(url).info()
        content_type = info.get('Content-Type')
        if 'text/html' in content_type:
            return True

        return False
    except:
        return None


def post_to_slaver_server(url, created_time, channel_id, is_powerup_domain=None):
    slaver_servers = get_slaver_servers()
    for server_name in slaver_servers:



        host = 'http://%s' % slaver_servers[server_name]['host']

        params = {'called_from': 'master',
                  'created_time': created_time,
                  'channel_id': channel_id,
                  'url': url}

        if is_powerup_domain is not None:
            host = 'http://%s/powerup' % slaver_servers[server_name]['host']

        requests.post(host, params=params)

    return True


def get_slaver_servers():
    slaver_servers = {}
    for server_name in settings.LOCATIONS:
        server_info = settings.LOCATIONS[server_name]
        if settings.MASTER_SERVER != server_info.get('host'):
            slaver_servers[server_name] = server_info

    return slaver_servers


def get_temporary_url(powerup_url):
    info = DOMAIN.find_one({'domain': powerup_url})
    if info:
        return info.get('temporary_domain')

    return '%s#' % powerup_url


def set_temporary_url(powerup_url, temporary_url):
    DOMAIN.update({'domain': powerup_url},
                  {'$set': {'temporary_domain': temporary_url}},
                  upsert=True)

    return True

