#! coding: utf-8


from rq import Queue
from redis import Redis
from time import strftime
from datetime import datetime
from urlparse import urlparse
from commands import getstatusoutput
from pymongo import MongoClient as MongoDB

import math
import pickle
import requests
import settings
import xmltodict

DATABASE = MongoDB(settings.MONGOD_SERVERS)[settings.DATABASE_NAME]
ANALYTICS = DATABASE.analytics

host, port ,db = settings.REDIS_SERVER.split(':')
REDIS_CONN = Redis(host=host, port=int(port), db=int(db))

host, port, db = settings.REDIS_ANALYTICS_QUEUE.split(':')
TASK_QUEUE = Redis(host=host, port=int(port), db=int(db))
CREATE_WEBPAGE_QUEUE = Queue('crawl_webpage',
                             connection=TASK_QUEUE,
                             default_timeout=600)


def get_time():
    now = '%s, %s %s, %s, %s' % (strftime("%a"), strftime("%b"),
                                 strftime("%d"), strftime("%Y"),
                                 strftime("%I:%M %p"))
    return now


def get_pagespeed_info(url):
    if url:
        pagespeed_url = '%s%s' % (settings.PAGESPEED_URL, url)
        pagespeed_info = requests.get(pagespeed_url).json()

        if pagespeed_info:
            webpage_info = ANALYTICS.find_one({'url': url})
            if webpage_info:
                ANALYTICS.update({'url': url},
                                 {'$set': {'pagespeed': pagespeed_info}})

            else:
                ANALYTICS.insert({'url': url,
                                 'pagespeed': pagespeed_info})

            REDIS_CONN.set('%s:pagespeed' % url,
                           pickle.dumps(pagespeed_info))

            return True

    return False


def get_yslow_info(url):
    if url:
        command = 'phantomjs %s --info all --format xml %s' % (settings.YSLOW_JS, url)
        status, output = getstatusoutput(command)
        if status == 0:
            yslow_info = xmltodict.parse(output).get('results')
            if yslow_info:
                webpage_info = ANALYTICS.find_one({'url': url})
                if webpage_info:
                    ANALYTICS.update({'url': url},
                                     {'$set': {'yslow': yslow_info}})

                else:
                    ANALYTICS.insert({'url': url,
                                      'yslow': yslow_info})

                REDIS_CONN.set('%s:yslow' % url,
                               pickle.dumps(yslow_info))

            return True

    return False


def get_harfile_info(url):
    if url:
        time_now = datetime.now().strftime('%Y-%m-%d+%H:%M:%S')
        host = urlparse(url).netloc
        filename = '%s+%s%s' % (host, time_now, '.com.har')
        dir = '%s%s' % (settings.HARSTORE, filename)

        command = 'phantomjs %s %s > %s' % (settings.NETSNIFF, url, dir)
        status, output = getstatusoutput(command)
        if status == 0:
            source_file = 'file/%s' % filename
            webpage_info = ANALYTICS.find_one({'url': url})
            if webpage_info:
                ANALYTICS.update({'url': url},
                                 {'$set': {'harfile': source_file}})

            else:
                ANALYTICS.insert({'url': url,
                                  'harfile': source_file})

            REDIS_CONN.set('%s:harfile' % url, source_file)

            return True

    return False


def get_webpage_info(url):
    pagespeed_info = REDIS_CONN.get('%s:pagespeed' % url)
    yslow_info = REDIS_CONN.get('%s:yslow' % url)
    harfile_info = REDIS_CONN.get('%s:harfile' % url)

    if all([pagespeed_info, yslow_info, harfile_info]):
        pagespeed_info = pickle.loads(pagespeed_info)
        yslow_info = pickle.loads(yslow_info)

        return {'pagespeed': pagespeed_info,
                'yslow': yslow_info,
                'harfile': harfile_info}

    else:
        webpage_info = ANALYTICS.find_one({'url': url})
        if webpage_info:
            return {'pagespeed': webpage_info.get('pagespeed'),
                    'yslow': webpage_info.get('yslow'),
                    'harfile': webpage_info.get('harfile')}

        else:
            CREATE_WEBPAGE_QUEUE.enqueue(get_pagespeed_info, url)
            CREATE_WEBPAGE_QUEUE.enqueue(get_yslow_info, url)
            CREATE_WEBPAGE_QUEUE.enqueue(get_harfile_info, url)

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

