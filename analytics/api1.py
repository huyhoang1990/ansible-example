#! coding: utf-8


from rq import Queue
from redis import Redis
from datetime import datetime
from urlparse import urlparse
from commands import getstatusoutput
from pymongo import MongoClient as MongoDB

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


def get_pagespeed_info(url):
    url = url.strip()
    if url:
        url = '%s%s' % (settings.PAGESPEED_URL, url)
        pagespeed_info = requests.get(url).json()

        if pagespeed_info:
            webpage_info = ANALYTICS.find_one({'url': url})
            if webpage_info:
                ANALYTICS.update({'url': url},
                                 {'$set': {'pagespeed': pagespeed_info}})

            else:
                ANALYTICS.insert({'url': url,
                                 'pagespeed': pagespeed_info})

            REDIS_CONN.set('%s:pagespeed', pagespeed_info)

            return True

    return False


def get_yslow_info(url):
    url = url.strip()
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

                REDIS_CONN.set('%s:yslow', yslow_info)

            return True

    return False


def get_harfile_info(url):
    url = url.strip()
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

            REDIS_CONN.set('%s:harfile', source_file)

            return True

    return False


def get_webpage_info(url):
    pagespeed_info = REDIS_CONN.get('%s:pagespeed' % url)
    yslow_info = REDIS_CONN.get('%s:yslow' % url)
    harfile_info = REDIS_CONN.get('%s:harfile' % url)

    if any([pagespeed_info, yslow_info, harfile_info]):
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

if __name__ == '__main__':
    url = 'http://google.com.vn'
    get_harfile_info(url)
