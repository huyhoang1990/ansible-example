

from pymongo import Connection, errors
from bson.objectid import ObjectId
import time

DATABASE_HOST = '127.0.0.1'
DATABASE_NAME = 'analytic'
DATABASE_PORT = 27017

CONNECTION = Connection(DATABASE_HOST, DATABASE_PORT)
DB = CONNECTION[DATABASE_NAME]

PAGESPEED = DB.pagespeed
YSLOW = DB.yslow
HAR = DB.har


def get_pagespeed_by_id(id):
    try:
        pagespeed_info = PAGESPEED.find_one({'_id': ObjectId(id)})
        return pagespeed_info
    except errors.OperationFailure, errors.ConnectionFailure:
        return False


def insert_pagespeed(url, dict_info):
    try:
        if not PAGESPEED.find_one({'url': url}):
            t = time.time()
            pagespeed_id = PAGESPEED.insert({
                'url': url,
                'info': dict_info,
                'time': t
            })
            return pagespeed_id
        else:
            return False
    except errors.ConnectionFailure:
        return False


def remove_pagespeed_by_id(id):
    try:
        PAGESPEED.remove({'_id': ObjectId(id)})
        return True
    except errors.ConnectionFailure:
        return False


def get_yslow_by_id(id):
    try:
        yslow_info = YSLOW.find_one({'_id': ObjectId(id)})
        return yslow_info
    except errors.OperationFailure, errors.ConnectionFailure:
        return False


def insert_yslow(url, dict_info):
    try:
        if not YSLOW.find_one({'url': url}):
            t = time.time()
            yslow_id = YSLOW.insert({
                'url': url,
                'info': dict_info,
                'time': t
            })
            return yslow_id
        else:
            return False
    except errors.ConnectionFailure:
        return False


def remove_yslow_by_id(id):
    try:
        YSLOW.remove({'_id': ObjectId(id)})
        return True
    except errors.ConnectionFailure:
        return False


def get_har_by_id(id):
    try:
        har_info = HAR.find_one({'_id': ObjectId(id)})
        return har_info
    except errors.OperationFailure, errors.ConnectionFailure:
        return False


def insert_har(url, directory):
    try:
        if not HAR.find_one({'url': url}):
            t = time.time()
            har_id = HAR.insert({
                'url': url,
                'directory': directory,
                'time': t
            })
            return har_id
        else:
            return False
    except errors.ConnectionFailure:
        return False


def remove_har_by_id(id):
    try:
        HAR.remove({'_id': ObjectId(id)})
        return True
    except errors.ConnectionFailure:
        return False
