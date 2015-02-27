#coding=utf8

HASH_SALT="ragrotardynamliumong"
DB_NAME="angle"

from xml.etree import ElementTree
import flask
import time
def E(msg=""):
    import json
    return json.dumps({"error":True,"msg":msg})

def A(msg=""):
    import json
    return json.dumps({"error":False,"msg":msg})

def encrypt(s):
    import hmac
    c=hmac.new(HASH_SALT)
    c.update(s)
    return c.hexdigest()
    
def now():
    return time.strftime('%Y-%m-%d %X',time.localtime(time.time()))

def is_admin():
    return flask.session.has_key('role') and flask.session['role'].find("admin")!=-1


def safe_split(s):
    if not isinstance(s,list):
        return s.split('|')
    return s



def parseWeixinXml(xml):
    '''
    input:
    <xml>
     <ToUserName><![CDATA[toUser]]></ToUserName>
     <FromUserName><![CDATA[fromUser]]></FromUserName> 
     <CreateTime>1348831860</CreateTime>
     <MsgType><![CDATA[text]]></MsgType>
     <Content><![CDATA[this is a test]]></Content>
     <MsgId>1234567890123456</MsgId>
     </xml>

     retrun :
     {'Content': 'this is a test',
     'CreateTime': '1348831860',
     'FromUserName': 'fromUser',
     'MsgId': '1234567890123456',
     'MsgType': 'text',
     'ToUserName': 'toUser'}
    '''
    return dict((child.tag, (child.text)) for child in ElementTree.fromstring(xml))


