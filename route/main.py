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
import qiniu.conf
import qiniu.io
import qiniu.rs
import re
import requests
import sys
import os
import weixin
import tool
import time
import math
import hashlib
from mongolog import logerr,log,MongoHandler
from jinja2 import Template
import thread
thread.start_new_thread
app = flask.Flask(__name__, static_folder='../static')
app.secret_key = encrypt('anglestreet2014')
app.config['UPLOAD_FOLDER'] = '../uploads'
# app.debug = True
app.logger.addHandler(MongoHandler())

import route_admin_shop
import route_admin_user
import route_weixin
import route_order
import route_print

@app.route('/api/listshop')
def listshop():
    w =Shop.objects(data__show=True).to_json()
    return w

@app.route("/api/session")
def session():
    return str(flask.session.items())

@app.route('/api/shop/<id>')
def shopinfo(id):
    return Shop.objects.with_id(ObjectId(id)).to_json()


@app.route('/api/submitorder',methods=['POST'])
def submitorder():

    if not flask.session.has_key('openid'):
        return E("找不到你的微信用户信息,请点击右上角关注我们的服务号“爱上天使街”")
    # flask.session['openid']='oqxGSuCUGMmLWehQxCbg9O-XqPzk'
    # flask.session['weixinname']='weixinname'
    c = flask.request.json
    o = Order()
    o.allcount = c['allcount']
    o.allprice = c['allprice']
    o.addr = c['addr']
    o.msg = c['msg']
    o.name = c['name']
    o.shopId = c['shopId']
    o.tel = c['tel']
    o.openid = flask.session['openid']
    o.weixinname = flask.session['weixinname']
    w = Shop.objects.with_id(c['shopId'])
    # 限制下单间隔时间
    oo = Order.objects(openid=o.openid).order_by("-_id").first()
    if oo:
        if (datetime.datetime.now() - oo.time).total_seconds() < 10:
            return E("下单太频繁,请稍后再试")
    for i in w.goods:
        if str(i.id) in c['goods']:
            b = Buy()
            b.category = i.category
            b.name = i.name
            b.price = i.price
            b.point = i.point 
            b.id = i.id
            b.count = int(c['goods'][str(i.id)])
            o.goods.append(b)

    o.info = w.info
    o.state = "verify"

    allcount = 0
    allprice = 0
    for i in o.goods:
        allcount += i.count
        allprice += i.price * i.count
    if allcount!=o.allcount or allprice!=o.allprice:
        return E("订单验证错误,可能在选购商品的时候店家修改了商品信息,建议重新从微信菜单进入购买")
    if allprice <=0:
        return E("订单金额太少")
    import json
    import random
    o.pid = len(Order.objects)*10+random.randrange(10)
    try:
        o.validate()
    except ValidationError as e:
        log.error(str(e))
        return E("你填写的信息不合法")
    o.detail.append(tool.now() + "成功下单,系统正在处理中")
    o.save()
    w.info.salesVolume += 1
    w.save()
    route_print.printOrder(o.id)
    weimsg = route_weixin.renderOrder(o)
    r,err = weixin.send_weixin(o.openid, weimsg)
    if r:
        o.state = 'pending'
        thread.start_new_thread(sendToShop, (o.id,) )
        o.save()
        return A("你的订单已经成功提交,订单详情已经发送的你的微信上,请查收")
    elif err==45015:
        o.state = "waiting"
        o.detail.append(tool.now()+" "+"微信通知发送不成功")
        o.save()
        return A("你的订单已经成功提交，由于你没有关注我们的微信号或者长时间没有操作，请关注我们的微信号并点击任意菜单。")
    else:
        log.error("服务器错误，请联系管理员"+o.to_json()+"\nweixinre:"+str(err))
        return E("服务器错误，请联系管理员") 


def renderToShopOrder(o):
    #remove customers mobile
    return  Template(u'''
你有新订单:
姓名:{{name}}
留言:{{msg}}
总件数:{{allcount}}
总价:{{allprice}}

店铺名称:{{info.name}}
店铺电话:{{info.tel}}

商品详情:
{% for i in goods%}{{i.name}}\t{{i.price}}*{{i.count}}={{i.price*i.count}}
{% endfor %}
处理详情:
{% for i in detail%}{{i.name}}{{i}}
{% endfor %}
请回复o{{pid}}确认订单
商品准备完毕之后，请回复p{{pid}}或者直接拨打我们的电话，我们的快递人员将马上和你联系。
    ''').render(json.loads(o.to_json()))


def sendToShop(id):
    o = Order.objects.with_id(id)
    if not o:
        log("send to shop not find id")
        return False,""
    shop = Shop.objects.with_id(o.shopId)
    openid = shop.info.weixin
    tel = shop.info.tel
    ok,msg = weixin.send_weixin(openid,renderToShopOrder(o))
    if ok==False:
        if msg==45015:
            ok,msg = weixin.send_sms(tel,"你的店铺有新的订单，请登录微信查看。")
            if ok : return True,"微信发送失败,用短信通知成功"
            else :return False,"微信发送失败,短信发送失败,错误编号"+str(msg)
        else :
            return False,"微信发送失败"+str(msg)
    return True,"微信发送成功"

@app.route('/api/admin/ordercmd',methods=['POST'])
def ordercmd():
    if not is_admin():return E("没有权限") 
    id = flask.request.json['id']
    cmd = flask.request.json['cmd']
    o = Order.objects.with_id(id)
    if cmd=='print':
        import route_print
        route_print.printOrder(o.id)
        return A("已经加入打印队列")
    if cmd=='noticeuser':
        weimsg = route_weixin.renderOrder(o)
        r,err = weixin.send_weixin(o.openid, weimsg)
        if r:
            return A("微信通知发送成功")
        elif err==45015:
            o.detail.append(tool.now()+" "+"微信通知发送不成功")
            return A("由于用户没有关注我们的微信号或者长时间没有操作,微信通知发送不成功.")
        else:
            log.error("服务器错误，请联系管理员"+o.to_json()+str(r))
            return E("微信通知发送不成功,错误编号:"+str(err)) 
    if cmd=='noticeshop':
        ok,msg = sendToShop(id)
        if ok: return A(msg)
        else :return E(msg)
    if cmd=='smsnoticeshop':
        tel = o.info.tel
        ok,msg = weixin.send_sms(tel,"你的店铺有新的订单，请登录微信查看。")
        if ok :return  A(msg)
        else: return E(msg)
    if cmd=="cancel":
        o.state="fail"
        o.save()
        return A("取消订单成功")
    return E("no such cmd")

@app.route('/api/admin/ordermodifystate',methods=['POST'])
def ordermodifystate():
    if not is_admin():return E("没有权限") 
    try:
        id = flask.request.json['id']
        state = flask.request.json['state']
        o = Order.objects.with_id(id)
        o.state = state
        o.save()
        return  A("修改成功")
    except Exception as e:
        log.error(e)
        return E("修改失败")


@app.route('/api/admin/log/<int:page>')
@app.route('/api/admin/log/count')
def adminlog(page=-1):
    if not is_admin():return E("没有权限") 
    page = int(page)
    if page==-1:
        return str(int(math.ceil(Log.objects.count()/50.)))
    return Log.objects.order_by("-_id")[page*50:50].to_json()


@app.route('/api/admin/backupdb')
def backupdb():
    if not is_admin():return E("没有权限") 
    j = {
        "Admin":Admin.objects.to_json(),
        "Shop":Shop.objects.to_json(),
        "Order":Order.objects.to_json(),
        "WeixinQueue":WeixinQueue.objects.to_json(),
        "Log":Log.objects.to_json(),
        "User":User.objects.to_json(),
        "PrintQueue":PrintQueue.objects.to_json()
    }
    return dumps(j)

@app.route('/static/css/mycss.css')
def static_css():
    return flask.send_file('../static/css/mycss.css',cache_timeout=0)

@app.route('/static/js/main.js')
def static_js():
    return flask.send_file('../static/js/main.js',cache_timeout=0)

@app.route('/')
@app.route('/<id1>')
@app.route('/<id1>/<id2>')
@app.route('/shop/<id2>/<id3>')
def index(id1="",id2="",id3=""):
    if config.Production:
        import route_weixin
        return route_weixin.jump()
    return flask.send_file('../index.html',cache_timeout=0)

@app.route('/admin')
@app.route('/admin/<p1>')
@app.route('/admin/<p1>/<p2>')
def admin(p1="",p2=""):
    return flask.send_file('../admin.html',cache_timeout=0)



if __name__ == "__main__":
    pass




