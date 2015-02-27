#coding=utf8

# 微信 oauth
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
import urllib2
from main import app
import hashlib
from jinja2 import Template
from mongolog import logerr, log


@app.route('/api/oauth')
def oauth():
    code = flask.request.args['code']
    j1 = json.loads(requests.get('https://api.weixin.qq.com/sns/oauth2/access_token?appid=' + config.APPID +
                                 '&secret=' + config.APPSECRET + '&code=' + code + '&grant_type=authorization_code').text)
    j2 = json.loads(requests.get('https://api.weixin.qq.com/sns/userinfo?access_token=' +
                                 j1['access_token'] + '&openid=' + j1['openid'] + '&lang=zh_CN').content)
    flask.session['openid'] = j1['openid']
    flask.session['weixinname'] = j2['nickname']
    u = User.from_json(dumps(j2))
    try:
        u.save()
    except:
        pass
    return flask.send_file('../index.html', cache_timeout=0)


@app.route('/api/jump')
def jump(id1="", id2="", id3=""):
    if flask.session.has_key('openid'):
        # weixin.send_weixin(flask.session['openid'], 'hello')
        return flask.send_file('../index.html', cache_timeout=0)
    if config.Production:
        r_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + config.APPID + '&redirect_uri=' + urllib2.quote(
            "http://anglestreet.duapp.com/api/oauth") + '&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'
    else:
        r_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + config.APPID + '&redirect_uri=' + urllib2.quote(
            "http://10.1.8.149:3000/api/oauth") + '&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'
    return flask.redirect(r_url)


@app.route('/api/admin/updatemenu')
def updatemenu():
    j = '''
    {
    "button": [
        {
            "type": "view", 
            "name": "外卖平台", 
            "url": "http://anglestreet.duapp.com/api/jump"
        }, 
        {
            "type": "view", 
            "name": "同城交友", 
            "url": "http://wsq.qq.com/reflow/209023638"
        },
        {
            "name": "菜单",
            "sub_button": [
                {
                    "type": "click", 
                    "name": "我的订单", 
                    "key": "myorder"
                }, 
                {
                    "type": "click", 
                    "name": "联系客服", 
                    "key": "kf"
                }, 
                {
                    "type": "view", 
                    "name": "关于我们", 
                    "url": "http://anglestreet.duapp.com/static/template/about.html"
                },
                {
                    "type":"view",
                    "name":"查看帮助",
                    "url": "http://anglestreet.duapp.com/static/help/help.html"
                },
                {
                    "type": "click", 
                    "name": "加入我们", 
                    "key": "joinme"
                }
            ]
        }
    ]
}
'''
    w = requests.post('https://api.weixin.qq.com/cgi-bin/menu/create?access_token=' + weixin.token_cache.get_token(),
                      j).text
    return w


@app.route('/weixin', methods=['POST', 'GET'])
def weixinroute():
    token = 'wefrewfewsgter'
    parm = flask.request.args.to_dict()
    if len(parm) == 0: return "no parm"
    ar = "".join(sorted([parm['nonce'], parm['timestamp'], token]))
    valid = hashlib.sha1(ar).hexdigest() == parm['signature']
    if flask.request.method == 'GET':
        if valid:
            return parm['echostr']
        return ""
    elif valid == False:
        return ""
    from weixin import Weixin

    weixinhandler = Weixin(token=token)
    params = weixinhandler.handle_request(flask.request.data)
    if params.has_key('MsgType') == False: return ""
    if params['MsgType'] == 'text':
        content = params['Content']
        openid = params['FromUserName']
        import re

        def to(content, openid, params):
            if content == '0':
                for i in WeixinQueue.objects(result='pending', openid=openid):
                    success, errorcode = weixin.send_weixin(i.openid, i.text, save=False)
                    if success:
                        i.result = "success"
                        i.save()
                return "查询成功"
            elif content == "id":
                return openid
            elif content == 'params':
                return str(params)
            elif content == 'info':
                return getinfo(openid)
            elif content == u'所有订单':
                orderall(openid)
                return "查询成功"
            elif re.match(r'^o\s*\d+$', content):
                # confirm order
                id = re.search(r'\d+', content).group()
                return confirmOrder(id, openid)
            elif re.match(r'^p\s*\d+$', content):
                # confirm order
                id = re.search(r'\d+', content).group()
                return completionOrder(id, openid)
            elif content == 'kf':
                weixinhandler.MsgType = 'transfer_customer_service'
                weixinhandler.text('kf')
                return weixinhandler.handle_response()
            else:
                # default reply
                weixinhandler.MsgType = 'transfer_customer_service'
                weixinhandler.text('kf')
                return weixinhandler.handle_response()

        weixinhandler.text(to(content, openid, params))
        return weixinhandler.handle_response()
    elif params['MsgType'] == 'event':

        # to do : when user focus check waiting order and send msg to shop
        if params['Event'] == 'CLICK':
            key = params['EventKey']
            openid = params['FromUserName']
            if key == 'kf':
                weixinhandler.MsgType = 'transfer_customer_service'
                weixinhandler.text('kf')
                return weixinhandler.handle_response()

            def click(key, openid):
                if key == "joinme": return joinme()
                if key == "aboutme": return aboutme()
                if key == "myorder": return myorder(openid)
                return "not find menu"

            weixinhandler.text(click(key, openid))
            weixinhandler.MsgType = 'Text'
            return weixinhandler.handle_response()

        # default reply
        weixinhandler.MsgType = 'transfer_customer_service'
        weixinhandler.text('kf')
        return weixinhandler.handle_response()
        #return ""


def confirmOrder(id, openid):
    try:
        w = Order.objects(pid=id)[0]
    except IndexError:
        return "找不到这个订单"
    if w.state == 'prepare':
        return "该订单已经被确认过"
    if w.state != 'pending' and w.state != 'waiting':
        return "该订单已经被确认过"
    s = Shop.objects.with_id(w.shopId).info.weixin
    if str(s) != openid:
        return "你没有确认此订单的权限"
    w.state = "prepare"
    w.detail.append(tool.now() + " " + "你的订单商户已经成功确认,请耐心等候")
    import thread

    thread.start_new_thread(weixin.send_weixin, (w.openid, u"你的订单已经被商户成功确认"))
    w.save()
    return str(id) + "号订单已经成功被确认"


def completionOrder(id, openid):
    try:
        w = Order.objects(pid=id)[0]
    except IndexError:
        return "找不到这个订单"
    if w.state == 'prepring' or w.state == 'delivery' or w.state == 'success':
        return "该订单已经在配送途中"
    s = Shop.objects.with_id(w.shopId).info.weixin
    if str(s) != openid:
        return "你没有确认此订单的权限"
    w.state = "prepring"
    w.detail.append(tool.now() + " " + "你的订单商家已经准备完成,我们正在准备配送")
    import thread

    thread.start_new_thread(weixin.send_weixin, (w.openid, u"你的订单商家已经准备完成,我们正在准备配送"))
    thread.start_new_thread(weixin.send_weixin, (config.admin_openid, u"订单" + w.pid + "商家已经准备完成,请安排配送人员"))
    import route_print

    route_print.printOrder(w._id)
    w.save()
    return str(id) + "号订单已经成功被确认"


def orderall(openid):
    w = Order.objects(openid=openid).order_by("-_id")[0:5]
    for i in w:
        weixin.send_weixin(openid, renderOrder(i))


def myorder(openid):
    w = Order.objects(openid=openid).order_by("-_id").first()
    if not w:
        return "没有找到你的订单信息"
    weimsg = renderOrder(w)
    return weimsg


def joinme():
    return '''合作加盟：
    请加创始人李先森的微信：lilinhan87之后发送以下信息：
    身份（商家/社会人士/学生）+联系方式+简单介绍（店铺/自身)+所在区域 稍后李先森将回复您。
'''


def aboutme():
    pass


def getinfo(openid):
    r = User.objects(openid=openid)
    if r:
        return r.to_json()
    token = weixin.token_cache.get_token()
    u = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s&lang=zh_CN' % (token, openid)
    w = requests.get(u).content
    s = User.from_json(w)
    if s.subscribe == 0:
        return ""
    try:
        s.save()
    except:
        pass
    return w


def renderOrder(o):
    return Template(u'''
你的订单如下:
联系电话:{{tel}}
姓名:{{name}}
留言:{{msg}}
总件数:{{allcount}}
总价:{{allprice}}

店铺名称:{{info.name}}
店铺电话:{{info.tel}}
配送地址:{{addr}}

商品详情:
{% for i in goods%}{{i.name}}\t{{i.price}}*{{i.count}}={{i.price*i.count}}
{% endfor %}
处理详情:
{% for i in detail%}{{i.name}}{{i}}
{% endfor %}
查看所有订单请回复 所有订单
    ''').render(json.loads(o.to_json()))


