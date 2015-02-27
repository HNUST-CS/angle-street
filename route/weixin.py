#coding=utf8
import datetime
import requests
import json
from config import APPID,APPSECRET,weimi_uid,weimi_pas
import time
from mongoengine import connect
from mongoengine.errors import ValidationError
from model import WeixinQueue
from mongolog import logerr,log

connect("angle")
class Token():
    '''
    获取并缓存access_token
    '''
    def __init__(self):
        self.refresh_token()
        self.expires = time.time()
    def refresh_token(self):
        URL_GET_TOKEN = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s"%(APPID,APPSECRET)
        r = requests.get(URL_GET_TOKEN).text
        self.token = json.loads(r)['access_token']

    def get_token(self):
        if time.time()-self.expires > 3600:
            self.refresh_token()
            self.expires = time.time()
        return self.token



token_cache = Token()


def send_weixin(openid,text,times=0,save=True):
    if times>3:
        log.error("weixin times to many")
        return False,"weixin times to many"
    w = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s"%token_cache.get_token()
    data = {
        "touser":openid,
        "msgtype":"text",
        "text":{
            "content":text
        }
    }
    r = requests.post(w,json.dumps(data,ensure_ascii=False).encode("utf8")).text
    r = json.loads(r)
    q = WeixinQueue()
    q.openid = openid
    q.text = text
    if r['errcode'] == 40001:
        token_cache.refresh_token()
        return send_weixin(openid, text,times+1)
    if r['errcode']!=0:
        q.result = "pending"
        q.errorId = r['errcode']
        if save: q.save()
        return False,r['errcode']
    q.result = "success"
    if save :q.save()
    return True,0


def send_sms(moble,content): 
    # todo  modify cid
    resp = requests.post(("http://api.weimi.cc/2/sms/send.html"),
    data={
        "uid": weimi_uid,
        "pas": weimi_pas,
        "mob": moble,
        "cid":"******",
        "type": "json"
    },timeout = 10 , verify = False)
    result = json.loads( resp.content )
    if result['code']==0: return True,""
    return False,result['msg']



import hashlib
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


class WeixinException(Exception):
    pass


class Weixin(object):
    def __init__(self, token=None):
        self.token = token
        self.MsgType = None
        self.FromUserName = None
        self.ToUserName = None
        self.CreateTime = None
        self.FuncFlag = None
        self.content = ''

    def verify_request(self, signature=None, timestamp=None,
                       nonce=None, echostr=None):
        if signature and timestamp and nonce and echostr:
            if not isinstance(timestamp, (str, unicode)):
                timestamp = str(timestamp)
            if self.token is None:
                raise WeixinException("token can not be None")
            args = [timestamp, self.token, nonce]
            args.sort()
            new_signature = hashlib.sha1(''.join(args)).hexdigest()
            if new_signature == signature:
                is_valid = True
            else:
                is_valid = False
            return is_valid, echostr

    def handle_request(self, body):
        root = ET.fromstring(body)
        Param_dict = dict()
        for elem in root:
            Param_dict[elem.tag] = elem.text
        if "CreateTime" in Param_dict:
            Param_dict["CreateTime"] = int(Param_dict["CreateTime"])
        if "MsgId" in Param_dict:
            Param_dict["MsgId"] = long(Param_dict["MsgId"])
        self.MsgType = Param_dict["MsgType"]
        self.ToUserName = Param_dict["ToUserName"]
        self.FromUserName = Param_dict["FromUserName"]
        self.CreateTime = Param_dict['CreateTime']
        self.FuncFlag = 0
        return Param_dict

    def handle_response(self, **kwargs):
        resp = {
            "ToUserName": kwargs.get("FromUserName", self.FromUserName),
            "FromUserName": kwargs.get("ToUserName", self.ToUserName),
            "CreateTime": kwargs.get("CreateTime", self.CreateTime),
            "MsgType": kwargs.get("MsgType", self.MsgType),
            "FuncFlag": kwargs.get("FuncFlag", self.FuncFlag)
        }
        resp = self._toxml(resp)
        xml_body = "<xml>" + resp + self.content + "</xml>"
        if isinstance(xml_body, unicode):
            xml_body.encode("utf-8")
        return xml_body

    def _cdata(self, s):
        return "<![CDATA[%s]]>" % s

    def _toxml(self, content):
        seq = []
        if isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, (unicode, str)):
                    seq.append("<%s>%s</%s>" % (key, self._cdata(value), key))
                elif isinstance(value, (list, dict)):
                    seq.append("<%s>%s</%s>" % (key, self._toxml(value), key))
                elif isinstance(value, int):
                    seq.append("<%s>%d</%s>" % (key, value, key))
                else:
                    raise WeixinException("type %s is not support in dict" %
                                          type(content))
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    seq.append("<%s>%s</%s>" % (self.tag, self._toxml(item), self.tag))
                else:
                    raise WeixinException("%s is not support in list" %
                                          type(content))
        else:
            raise WeixinException("%s is not support in content" %
                                  type(content))

        return ''.join(seq)

    def music(self, content):
        for key in ["Title", "Description", "MusicUrl", "HQMusicUrl"]:
            if key not in content:
                raise WeixinException("%s can't be None" % key)
        self.content = self._toxml(dict(Music=content))
    
    def news(self, content):
        articles = len(content)
        self.tag = "item"
        self.content = "<ArticleCount>%d</ArticleCount>" % articles
        self.content += self._toxml(dict(Articles=content))

    def text(self, content):
        self.content = self._toxml(dict(Content=content))