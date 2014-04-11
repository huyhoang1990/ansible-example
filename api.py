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
from time import strftime, sleep
import xmltodict
import json
import math
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


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


def generate_har(url):
    profile = webdriver.FirefoxProfile()
    try:
        profile.add_extension(extension='resources/firebug-1.12.7.xpi')
        profile.add_extension(extension='resources/netExport-0.8.xpi')

        profile.set_preference("app.update.enabled", "false")
        domain = "extensions.firebug."

        #  Set default Firebug preferences
        profile.set_preference(domain + "currentVersion", "2.0")
        profile.set_preference(domain + "allPagesActivation", "on")
        profile.set_preference(domain + "defaultPanelName", "net")
        profile.set_preference(domain + "net.enableSites", "true")

        #  Set default NetExport preferences
        profile.set_preference(domain + "netexport.alwaysEnableAutoExport", "true")
        profile.set_preference(domain + "netexport.showPreview", "true")
        profile.set_preference(domain + "netexport.defaultLogDir", "/var/www/har/file")

        driver = webdriver.Firefox(profile)
        try:
            sleep(6)
            driver.get(url)
            sleep(10)
            driver.close()
        except WebDriverException:
            return False
    except IOError:
        return False