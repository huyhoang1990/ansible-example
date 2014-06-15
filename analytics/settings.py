#! coding: utf-8


REDIS_SERVER = '127.0.0.1:6379:0'

REDIS_ANALYTICS_QUEUE = '127.0.0.1:6379:1'

SECRET_KEY = 'bf4b484c-ca9c-11e3-993b-1a514932ac01'

PAGESPEED_URL = 'https://www.googleapis.com/pagespeedonline/v1/runPagespeed?url='

MONGOD_SERVERS = "127.0.0.1:27017"

DATABASE_NAME = 'webpage_analytics'

YSLOW_JS = '/static/js/yslow.js'

HARSTORE = '/srv/harviewer/files/'

NETSNIFF = '/static/js/netsniff.js'

LOADREPORT = '/srv/loadreport'

# HAR_SERVER = 'http://127.0.0.1:8080/har/pagelist.php?path='


LOCATIONS = {
    'Ha Noi': {'host': '10.2.14.22', 'id': 'hn'},
    'Ho Chi Minh': {'host': '10.2.14.24', 'id': 'hcm'}
}


MASTER_SERVER = '10.2.14.22'
