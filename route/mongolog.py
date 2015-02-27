#coding=utf8

import logging
from datetime import datetime
from pymongo.connection import Connection
from bson import InvalidDocument
from model import Log
import config
from json import dumps
import flask
import traceback  

Log.objects._collection.safe=False

from logging import Formatter

class MongoHandler(logging.Handler):
    @classmethod
    def to(cls,  level=logging.NOTSET):
        return cls(level)
        
    def __init__(self,level=logging.NOTSET):
        logging.Handler.__init__(self, level)

    def emit(self,record):
        """ Store the record to the collection. Async insert """
        l = Log()
        l.msg = str(record.msg)+ str(record.args)+str(traceback.format_exc())
        l.filename = record.filename
        l.name = record.name 
        l.levelno = record.levelno
        l.levelname = record.levelname
        if flask.request:
            w = flask.request
            l.json = dumps(w.json,ensure_ascii=False)
            l.url = w.url
            l.session = str(flask.session.items())
            l.ua = w.user_agent.string
            l.ip = w.remote_addr
        l.save()


log = logging.getLogger('main')
log.setLevel(logging.DEBUG)
log.addHandler(MongoHandler())

def logerr(func):
    def _logerr(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
            return ret
        except:
            log.error(traceback.format_exc())
            raise
    return _logerr
 
