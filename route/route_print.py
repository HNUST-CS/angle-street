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
import hashlib
from mongolog import logerr,log,MongoHandler
from jinja2 import Template
from main import app

@app.route('/api/admin/print/task',methods=['POST'])
def listtask():
    j = json.loads(flask.request.form['data'])
    key = j['key']
    okid = j['okid']

    if key != "wasd": E("password error")
    for i in okid :
        p = PrintQueue.objects.with_id(i)
        p.state = "ok"
        p.save()
    return PrintQueue.objects(state="wait").to_json()

def printOrder(id):
    p = PrintQueue()
    p.content = renderOrder(id)
    p.state = "wait"
    p.save()

def renderOrder(id):
    o = Order.objects.with_id(id)
    s = json.loads(o.to_json())
    s['time'] = o.time.strftime("%Y-%m-%d %H:%M:%S")
    for i in s['goods']:
        b = i['name']+u'#'+u"%s元x%s份=%s元"%(i['price'],i['count'],i['price']*i['count'])
        w = len(re.findall(r'[^\ux00-\uxff]',b))+len(b)
        i['text']=b.replace('#', ' '*(35-w))
    return  Template(u'''
爱上天使街外卖平台外卖小票
=============================
销售单号:{{pid}}(顾客联)
流水号:{{_id['$oid']}}
顾客名称:{{name}}({{weixinname}})
联系电话:{{tel}}
留言:{{msg}}
店铺名称:{{info.name}}
店铺电话:{{info.tel}}
配送地址:{{addr}}
------------------------------
商品详情:
{% for i in goods%}{{i.text}}
{% endfor %}
=============================
总件数:{{allcount}}件
总价:{{allprice}}元
销售时间:{{time}}
客服电话:13333333333

















=============================
        ''').render(s)


# print renderOrder('53e736954bca24362a85f046').encode('utf8')
