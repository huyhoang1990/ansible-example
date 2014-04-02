__author__ = 'thanhdl'

import settings
import requests
from commands import getstatusoutput
from time import strftime


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
        command = 'phantomjs %s --info all %s' % (settings.YSLOW_JS, url)
        status, output = getstatusoutput(command)
        if status == 0:
            return output.json()
        else:
            return False
    else:
        return False