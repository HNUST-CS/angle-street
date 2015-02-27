#coding=utf8

#微信
APPID = ''
APPSECRET = ''
#七牛
QINIU_ACCESS_KEY = ""
QINIU_SECRET_KEY = ""

#bae
api_key = ""
secret_key = ""
db_name = ""

redis_db_name = ''
redis_myauth = "%s-%s-%s"%(api_key, secret_key, redis_db_name)

weimi_uid = ""
weimi_pas = ""

admin_openid = ''


print_local_key = ""

from mongoengine import connect
import os
#是否生产环境
Production = "bae/3.0" == os.environ.get("SERVER_SOFTWARE")
if Production:
    connect(db_name,host= "mongo.duapp.com", port= 8908,username=api_key,password=secret_key)
    
else :
    connect("angle")
