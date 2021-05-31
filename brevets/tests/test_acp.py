"""
Nose tests for acp_times.py
"""
from acp_times import *
import os
from pymongo import MongoClient
import config

import nose    # Testing framework
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.WARNING)
log = logging.getLogger(__name__)

#CONFIG = config.configuration()
client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.tododb


def test_zero_distance():
    opent = open_time(0, 0, arrow.get('1970-01-01T00:00:00.000Z')).format('YYYY-MM-DDTHH:mm')
    closet = close_time(0, 0, arrow.get('1970-01-01T00:00:00.000Z')).format('YYYY-MM-DDTHH:mm')
    assert opent == "1970-01-01T00:00"
    assert closet == "1970-01-01T01:00"

def test_example():
    assert open_time(175, 200, arrow.get('1970-01-01T00:00:00.000Z')).format('YYYY-MM-DDTHH:mm') == '1970-01-01T05:09'
    assert close_time(175, 200, arrow.get('1970-01-01T00:00:00.000Z')).format('YYYY-MM-DDTHH:mm') == '1970-01-01T11:40'

def test_db():
    media = db.media
    doc1 = {"Author": "George RR Martin", "Series": "ASOIAF", "Show": "Game of Thrones", "Seasons": 8}
    doc2 = {"Author": "Rick Riordan", "Series": "Percy Jackson"}
    media.insert_one(doc1)
    media.insert_one(doc2)
    q1 = media.find_one({"Author": "Rick Riordan"})
    q2 = media.find_one({"Author": "JK Rowling"})
    assert q1
    assert q2 is None
