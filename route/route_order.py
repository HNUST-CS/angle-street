#coding=utf8
from tool import *
from bson.json_util import dumps
from bson.objectid import ObjectId
from model import *
from mongoengine import connect
from mongoengine.errors import ValidationError
import config
import flask
import json
import pymongo
import re
import requests
import sys
import os
import weixin
import tool
import time

from main import app
from bson.json_util import dumps
from mongolog import logerr,log

@app.route('/api/admin/listorder/<state>')
@app.route('/api/admin/listorder/<state>/<int:start>')
def orderlistall(state,start=0):
    if start==-1 :
        return len(Order.objects(state=state))
    if state=="all":
        return Order.objects()[start*50:start*50+50].to_json()
    return Order.objects(state=state)[start*50:start*50+50].to_json()




