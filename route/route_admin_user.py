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

# admin
@app.route("/api/login",methods=['POST'])
def login():
    try:
        username=flask.request.json['username']
        passwd=flask.request.json['passwd']
    except :
        return E("请填写完整")
    p = encrypt(passwd)
    r = Admin.objects(username=username)
    if not r:
        return E("用户不存在")
    r = r[0]
    if r.passwd !=p:
        return E("​密码错误")
    flask.session.clear()
    flask.session['username']=r.username
    flask.session['role']=r.role
    return json.dumps({"error":False,"msg":"登陆成功","username":r.username})

@app.route('/api/logout')
def logout():
    flask.session.clear()
    return A()


@app.route('/api/islogin')
def islogin():
    try:
        if len(flask.session['username'])>0:
            return json.dumps({"error":False,"msg":"登陆成功","username":flask.session['username']})
    except KeyError:
        return E("你没有登陆")




@app.route('/api/admin/listuser')
def listuser():
    if is_admin():
        return Admin.objects.exclude("passwd").to_json()
    return E("没有权限")


@app.route('/api/admin/adduser',methods=['POST'])
def adduser():
    if not is_admin():return E("没有权限") 
    j=flask.request.json
    if len(Admin.objects(username=j['username'])):
        return E("用户已经存在了")
    if len(j['passwd'])<6:
        return E("密码太短")
    j['passwd'] = encrypt(j['passwd'])
    try:
        r = Admin.from_json(dumps(j))
        r.save()
    except ValidationError as e:
        return E("验证错误"+str(e))
    return A()


@app.route('/api/admin/deluser',methods=['POST'])
def deluser():
    if not is_admin():return E("没有权限") 
    username = flask.request.json['username']
    if username == 'admin': return E('此用户无法删除')
    r = Admin.objects(username=username)
    if not r:
        return E("用户不存在")
    r.delete()
    return A("删除成功")


@app.route('/api/admin/updateuser',methods=['POST'])
def updateuser():
    if not is_admin():return E("没有权限") 
    w = flask.request.json
    username = w['username']
    msg=""
    r = Admin.objects(username=username)
    if not r:
        return E("用户不存在")
    if w.has_key('passwd')==False or len(w['passwd'])==0:
        msg="更新成功"
    else : 
        w['passwd'] = encrypt(w['passwd'])
        r.passwd = w['passwd']
        msg="密码修改成功"
    r=r[0]
    r.username = w['username']
    r.comment = w['comment']
    r.role = w['role']
    r.tel = w['tel']
    r.qq = w['qq']
    if r.validate():
        E("验证错误")
    r.save()
    return A(msg)

