#! coding: utf-8
__author__ = 'thanhdl'

"""
Nhớ cài phantomjs
Nhớ cài xmltodict
pip install xmltodict
"""

import settings
import requests
from commands import getstatusoutput
from time import strftime
import xmltodict
import json
import math
import database


def get_time():
    now = '%s, %s %s, %s, %s' % (strftime("%a"), strftime("%b"),
                                 strftime("%d"), strftime("%Y"),
                                 strftime("%I:%M %p"))
    return now


def pagespeed(url):
    if url:
        url = '%s%s' % (settings.API_URL, url)
        result = requests.get(url)
        if result:
            return result.json()
        else:
            return False
    else:
        return False


def yslow(url):
    if url:
        command = 'phantomjs %s --info all --format xml %s' % (settings.YSLOW_JS, url)
        status, output = getstatusoutput(command)
        if status == 0:
            result = json.dumps(xmltodict.parse(output))
            return json.loads(result)['results']
        else:
            return False
    else:
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


def har_viewer(url):
    if url:
        command = 'phantomjs %s %s > %s' % (settings.NETSNIFF, url, settings.HARSTORE)
        status, output = getstatusoutput(command)
        if status == 0:
            return settings.HARSTORE
        else:
            return False
    else:
        return False