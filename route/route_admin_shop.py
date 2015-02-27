#coding=utf8
from tool import *
from bson.json_util import dumps
from bson.objectid import ObjectId
from model import *
from mongoengine import connect
from mongoengine.errors import ValidationError
import flask
import json
import re
import requests
import sys
import os
import tool
import time
from main import app
import config
import qiniu.conf
import qiniu.rs
import qiniu.io
from mongolog import logerr,log

QINIU_BUCKET = 'anglestreet'
qiniu.conf.ACCESS_KEY = config.QINIU_ACCESS_KEY
qiniu.conf.SECRET_KEY = config.QINIU_SECRET_KEY

@app.route('/api/admin/listshop')
def admin_listshop():
    if not is_admin():return E("没有权限") 
    return Shop.objects.to_json()

@app.route('/api/admin/shopinfo/<id>')
def admin_shopinfo(id):
    if not is_admin():return E("没有权限") 
    return Shop.objects.with_id(ObjectId(id)).to_json()

@app.route('/api/admin/addshop',methods=['POST'])
def admin_addshop():
    if not is_admin():return E("没有权限") 
    try:
        w=flask.request.json
        w['data']['salesVolume']=0
        w['info']['city']=safe_split(w['info']['city'])
        w['data']['admin']=safe_split(w['data']['admin'])
        w['goods']=[]
        c = Shop.from_json(dumps(w))
        c.save()
    except ValidationError as e:
        return E("验证错误")
    return A("修改成功")

@app.route('/api/admin/updateshop',methods=['POST'])
def admin_updateshop():
    if not is_admin():return E("没有权限") 
    w = flask.request.json
    del w['_id']
    id = w['id']
    r = Shop.objects.with_id(ObjectId(id))
    if not r:
        return E("店铺不存在")

    w['info']['city']=safe_split(w['info']['city'])
    w['data']['admin']=safe_split(w['data']['admin'])

    r.info=Info().from_json(dumps(w['info']))
    r.data.star = w['data']['star']
    r.data.proority = w['data']['proority']
    r.data.show = w['data']['show']
    r.data.admin = safe_split(w['data']['admin'])
    r.save()
    return A("修改成功")

@app.route('/api/admin/updateshopgoods',methods=['POST'])
def updateshopgoods():
    if not is_admin():return E("没有权限")
    w = flask.request.json
    id = w['id']
    r = Shop.objects.with_id(ObjectId(id))
    del w['_id']
    if not r:
        return E("店铺不存在")
    l = []
    for i in w['goods']:
        l.append(i['id'])
    if len(set(l))!=len(l):
        return E("ID不唯一,修改失败")
    t = Shop().from_json(dumps(w))
    r.info.city=safe_split(r.info.city)
    r.data.admin=safe_split(r.data.admin)
    r.info=Info().from_json(dumps(w['info']))
    r.goods = t.goods
    # import ipdb;ipdb.set_trace()
    r.save()
    return A("修改成功")


@app.route('/api/admin/upload',methods=['POST'])
def upload():
    if not is_admin():return E("没有权限") 
    w = flask.request.files['file']
    policy = qiniu.rs.PutPolicy(QINIU_BUCKET)
    uptoken = policy.token()
    ret, err = qiniu.io.put(uptoken, None, w)
    ret['url']=ret['key']
    if err :return E("图片上传失败")
    return dumps(ret)

@app.route('/api/admin/delshop',methods=['POST'])
def delshop():
    if not is_admin():return E("没有权限")
    w = flask.request.json
    id = w['id']
    r = Shop.objects.with_id(ObjectId(id))
    if len(r.goods)>0:
        return E("必须先删除该店铺所有商品之后才能删除店铺")
    r.delete()
    return A("删除成功")

@app.route('/api/admin/filteropenid/<id>')
def filteropenid(id):
    w = User.objects(openid__startswith=id)
    if len(w)==1:
        return w[0].openid
    return id