#coding=utf8
from mongoengine import *
import datetime
class Admin(Document):
    username = StringField(max_length=40,regex=r'^[a-zA-Z0-9]{0,30}$',required=True,unique=True)
    passwd = StringField(max_length=50,required=True)
    comment = StringField(max_length=999,required=True)
    role = StringField(max_length=50,required=True,default="")
    tel = StringField(max_length='11',regex=r'^\d{11}$',required=True)
    qq = StringField(max_length='11',regex=r'^\d{6,12}$',required=True)

class Info(EmbeddedDocument):
    name = StringField(max_length=100,required=True)
    tel = StringField(max_length=100,required=True)
    city = ListField(StringField(max_length=100,required=True),required=True)
    shopImg = StringField(max_length=100,required=True)
    deliveryTime = StringField(max_length=100,required=True)
    freePrice =  StringField(max_length=100,required=True)
    area =  StringField(max_length=100,required=True)
    addPrice =  StringField(max_length=100,required=True)
    state =  StringField(max_length=100,required=True)
    startPrice =  StringField(max_length=100,required=True)
    msg =  StringField(max_length=100,required=True)
    shortName =  StringField(max_length=100,required=True)
    desc =  StringField(max_length=100,required=True)
    addr =  StringField(max_length=100,required=True)
    weixin = StringField(required=True)

class Goods(EmbeddedDocument):
    id = IntField(required=True)
    name = StringField(max_length=50,required=True)
    category = StringField(max_length=20,required=True)
    img = StringField(max_length=1111,required=True)
    show = BooleanField(required=True,default=True)
    price = FloatField(required=True,default=0)
    salesVolume = IntField(required=True,default=0)
    point = IntField(required=True,default=0)
    desc = StringField(max_length=500,required=True)
    showinfo = BooleanField(required=False,default=False)

class Data(EmbeddedDocument):
    admin = ListField(StringField(max_length=40),required=False)
    star = IntField(max_value=5,min_value=0,required=True)
    salesVolume = IntField(required=True,default=0)
    proority = IntField(required=True,default=0)
    show = BooleanField(required=True,default=True)

class Shop(Document):
    info = EmbeddedDocumentField(Info,required=True)
    goods = ListField(EmbeddedDocumentField(Goods),default=[])
    data = EmbeddedDocumentField(Data,required=True)
    shopImg = StringField(max_length=100,default="1",required=True)



class Buy(EmbeddedDocument):
    name = StringField(max_length=50,required=True)
    category = StringField(max_length=20,required=True)
    price = FloatField(required=True,default=0)
    point = IntField(required=True,default=0)
    id = IntField(required=True)
    count = IntField(required=True,default=0,max_value=9999)



class Order(Document):
    pid = IntField(required = True)
    info = EmbeddedDocumentField(Info,required=True)
    addr = StringField(max_length=200,required=True)
    allcount = IntField(max_value=9999,min_value=0,required=True)
    allprice = IntField(max_value=99999,min_value=0,required=True)
    msg = StringField(max_length=200,required=True)
    name = StringField(max_length=200,required=True)
    weixinname = StringField(max_length=200,required=True)
    openid = StringField(max_length=200,required=True)
    shopId = StringField(max_length=200,required=True)
    tel = StringField(max_length=200,required=True)
    goods = ListField(EmbeddedDocumentField(Buy),required=True)
    state = StringField(max_length=100,required=True)
    detail = ListField(StringField(max_length=500,required=True))
    time = DateTimeField(default=datetime.datetime.now)
    couriername = StringField(max_length=200,required=True,default="")
    couriertel = StringField(max_length=200,required=True,default="")
 
class WeixinQueue(Document):
    time = DateTimeField(default=datetime.datetime.now)
    openid = StringField(max_length=200,required=True)
    text = StringField(max_length=3000,required=True)
    errorId = IntField()
    result = StringField(max_length=200,required=True)


class Log(Document):
    time = DateTimeField(default=datetime.datetime.now)
    filename = StringField(max_length=200,required=True)
    msg = StringField(max_length=2000,required=True)
    levelno = IntField()
    name = StringField(max_length=2000,required=True)  
    levelname= StringField(max_length=20,required=True)  

    json = StringField(max_length=20000,required=False)
    url = StringField(max_length=200,required=False)
    session = StringField(max_length=2000,required=False)
    ua = StringField(max_length=200,required=False)
    ip = StringField(max_length=200,required=False)


class User(Document):
    openid = StringField(max_length=200,required=True)
    subscribe = IntField()
    nickname = StringField(max_length=200,required=True)
    sex = IntField()
    language = StringField(max_length=200,required=True)
    city = StringField(max_length=200,required=True)
    province = StringField(max_length=200,required=True)
    country = StringField(max_length=200,required=True)
    headimgurl = StringField(max_length=400,required=True)
    subscribe_time =IntField(default=0)


class PrintQueue(Document):
    content = StringField(max_length=4000,required=True)
    time = DateTimeField(default=datetime.datetime.now)
    state = StringField(max_length=20,required=True)

if __name__ == "__main__":

    s='''
    {
        "info" : {
            "city" : [ 
                "湖南省", 
                "湘潭市", 
                "湖南科技大学"
            ],
            "tel" : "15273271639",
            "name" : "正宗浏阳特色蒸菜",
            "shopImg" : "Ftg7Avi_Oxu8deleWvgv8k0ldtcG",
            "deliveryTime" : "50",
            "freePrice" : "6",
            "area" : "湖南科技大学",
            "addPrice" : "0",
            "state" : "营业",
            "startPrice" : "6",
            "msg" : "暑假正常营业",
            "shortName" : "zzlyzcg",
            "desc" : "正宗浏阳特色蒸菜",
            "addr" : "湖南省|湘潭市|湖南科技大学"
        },
        "goods" : [ 
            {
                "category" : "荤菜",
                "name" : "蒸扣肉",
                "img" : "1",
                "show" : true,
                "price" : "7",
                "point" : 0,
                "salesVolume" : 11,
                "id" : 1,
                "desc" : ""
            }, 
            {
                "category" : "荤菜",
                "name" : "蒸腊鸡",
                "img" : "",
                "show" : true,
                "price" : "7",
                "point" : 0,
                "salesVolume" : 11,
                "id" : 2,
                "desc" : ""
            }, 
            {
                "category" : "荤菜",
                "name" : "蒸腊肉",
                "img" : "",
                "show" : true,
                "price" : "7",
                "point" : 0,
                "salesVolume" : 1,
                "id" : 3,
                "desc" : ""
            }, 
            {
                "category" : "荤菜",
                "name" : "手撕鱼",
                "img" : "",
                "show" : false,
                "price" : "7",
                "point" : 0,
                "salesVolume" : 22,
                "id" : 4,
                "desc" : ""
            }, 
            {
                "category" : "荤菜",
                "name" : "口味鸡",
                "img" : "",
                "show" : true,
                "price" : "7",
                "point" : 0,
                "salesVolume" : 33,
                "id" : 5,
                "desc" : ""
            }, 
            {
                "category" : "荤菜",
                "name" : "酸豆角炒肉",
                "img" : "",
                "show" : true,
                "price" : "7",
                "point" : 0,
                "salesVolume" : 444,
                "id" : 6,
                "desc" : ""
            }, 
            {
                "category" : "荤菜",
                "name" : "外婆菜炒肉",
                "img" : "",
                "show" : true,
                "price" : "7",
                "point" : 0,
                "salesVolume" : 555,
                "id" : 7,
                "desc" : ""
            }, 
            {
                "category" : "荤菜",
                "name" : "家常豆腐",
                "img" : "Ftg7Avi_Oxu8deleWvgv8k0ldtcG",
                "show" : true,
                "price" : "7",
                "point" : 0,
                "salesVolume" : 66,
                "id" : 8,
                "desc" : ""
            }, 
            {
                "category" : "荤菜",
                "name" : "红烧日本豆腐",
                "img" : "",
                "show" : true,
                "price" : "7",
                "point" : 0,
                "salesVolume" : 777,
                "id" : 9,
                "desc" : ""
            }, 
            {
                "category" : "小菜",
                "name" : "小白菜",
                "img" : "",
                "show" : true,
                "price" : "3",
                "point" : 0,
                "salesVolume" : 0,
                "id" : 10,
                "desc" : ""
            }, 
            {
                "category" : "小菜",
                "name" : "清炒藕片",
                "img" : "",
                "show" : true,
                "price" : "3",
                "point" : 0,
                "salesVolume" : 0,
                "id" : 11,
                "desc" : ""
            }, 
            {
                "category" : "小菜",
                "name" : "土豆丝",
                "img" : "",
                "show" : true,
                "price" : "3",
                "point" : 0,
                "salesVolume" : 0,
                "id" : 12,
                "desc" : ""
            }, 
            {
                "category" : "小菜",
                "name" : "红烧豆腐",
                "img" : "",
                "show" : true,
                "price" : "7",
                "point" : 0,
                "salesVolume" : 0,
                "id" : 13,
                "desc" : ""
            }, 
            {
                "category" : "小菜",
                "name" : "茄子豆角",
                "img" : "",
                "show" : true,
                "price" : "4",
                "point" : 0,
                "salesVolume" : 0,
                "id" : 14,
                "desc" : ""
            }, 
            {
                "category" : "小菜",
                "name" : "干煸四季豆",
                "img" : "",
                "show" : true,
                "price" : "4",
                "point" : 0,
                "salesVolume" : 0,
                "id" : 15,
                "desc" : ""
            }, 
            {
                "category" : "小菜",
                "name" : "蛋炒饭",
                "img" : "",
                "show" : true,
                "price" : "5",
                "point" : 0,
                "salesVolume" : 0,
                "id" : 16,
                "desc" : ""
            }, 
            {
                "category" : "小菜",
                "name" : "现炒大盆青菜",
                "img" : "",
                "show" : true,
                "price" : "7",
                "point" : 0,
                "salesVolume" : 0,
                "id" : 17,
                "desc" : ""
            }, 
            {
                "category" : "小菜",
                "name" : "肉炒饭",
                "img" : "",
                "show" : true,
                "price" : "7",
                "point" : 0,
                "salesVolume" : 0,
                "id" : 18,
                "desc" : ""
            }, 
            {
                "category" : "小菜",
                "name" : "红烧豆腐",
                "img" : "",
                "show" : true,
                "price" : "7",
                "point" : 0,
                "salesVolume" : 0,
                "id" : 19,
                "desc" : ""
            }, 
            {
                "category" : "小菜",
                "name" : "土豆丝",
                "img" : "",
                "show" : true,
                "price" : "3",
                "point" : 0,
                "salesVolume" : 0,
                "id" : 20,
                "desc" : ""
            }, 
            {
                "category" : "小菜",
                "name" : "豆皮",
                "img" : "",
                "show" : true,
                "price" : "7",
                "point" : 0,
                "salesVolume" : 0,
                "id" : 21,
                "desc" : ""
            }, 
            {
                "category" : "小菜",
                "name" : "海带丝",
                "img" : "",
                "show" : true,
                "price" : "3",
                "point" : 0,
                "salesVolume" : 0,
                "id" : 22,
                "desc" : ""
            }, 
            {
                "category" : "小菜",
                "name" : "土豆片",
                "img" : "",
                "show" : true,
                "price" : "3",
                "point" : 0,
                "salesVolume" : 0,
                "id" : 23,
                "desc" : ""
            }, 
            {
                "category" : "小菜",
                "name" : "冬瓜",
                "img" : "",
                "show" : true,
                "price" : "7",
                "point" : 0,
                "salesVolume" : 0,
                "id" : 24,
                "desc" : ""
            }, 
            {
                "category" : "小菜",
                "name" : "蒸蛋",
                "img" : "",
                "show" : true,
                "price" : "3",
                "point" : 0,
                "salesVolume" : 0,
                "id" : 25,
                "desc" : ""
            }, 
            {
                "category" : "小菜",
                "name" : "包菜",
                "img" : "",
                "show" : true,
                "price" : "3",
                "point" : 0,
                "salesVolume" : 0,
                "id" : 26,
                "desc" : ""
            }
        ],
        "shopImg" : "",
        "goodsize" : 0,
        "data" : {
            "admin" : ["admin"],
            "star" : "5",
            "salesVolume" : 0,
            "proority" : "0",
            "show" : true
        },
        "id" : "53d346584bca243353216e2a"
    }'''

    # print Shop().from_json(s).validate()
