import pymongo

__author__ = 'thanhdl'

from pymongo import Connection, errors
from bson.objectid import ObjectId

DATABASE_HOST = '127.0.0.1'
DATABASE_NAME = 'test'
DATABASE_PORT = 27017

connection = Connection(DATABASE_HOST, DATABASE_PORT)
db = connection[DATABASE_NAME]

pagespeedcollection = db.pagespeedcollection
yslowcolletion = db.yslowcolletion
harviewercollection = db.harviewercollection


def get_pagespeed_by_id(id):
    try:
        result = pagespeedcollection.find_one({'_id': ObjectId(id)})
        return result
    except errors.OperationFailure, errors.ConnectionFailure:
        return False


def insert_pagespeed(url, title, status_code, dict_info):
    try:
        result = pagespeedcollection.insert({
            'url': url,
            'title': title,
            'status_code': status_code,
            'info': dict_info
        })
        return result
    except errors.ConnectionFailure:
        return False


def remove_pagespeed_by_id(id):
    try:
        result = pagespeedcollection.remove({'_id': ObjectId(id)})
        return True
    except errors.ConnectionFailure:
        return False


def get_yslow_by_id(id):
    try:
        result = yslowcolletion.find_one({'_id': ObjectId(id)})
        return result
    except errors.OperationFailure, errors.ConnectionFailure:
        return False


def insert_yslow(url, dict_info):
    try:
        result = yslowcolletion.insert({
            'url': url,
            'info': dict_info
        })
        return result
    except errors.ConnectionFailure:
        return False


def remove_yslow_by_id(id):
    try:
        result = yslowcolletion.remove({'_id': ObjectId(id)})
        return True
    except errors.ConnectionFailure:
        return False


def get_harviewer_by_id(id):
    try:
        result = harviewercollection.find_one({'_id': ObjectId(id)})
        return result
    except errors.OperationFailure, errors.ConnectionFailure:
        return False


def insert_harviewer(url, dict_info):
    try:
        result = harviewercollection.insert({
            'url': url,
            'info': dict_info
        })
        return result
    except errors.ConnectionFailure:
        return False


def remove_harviewer_by_id(id):
    try:
        result = harviewercollection.remove({'_id': ObjectId(id)})
        return True
    except errors.ConnectionFailure:
        return False
