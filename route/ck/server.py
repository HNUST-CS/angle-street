#coding=utf8
from flask import Flask  
from flask import request
import json
import collections
import web
import web.db
import datetime
from flask import render_template

app=Flask(__name__)

db = web.database(
    dbn='mysql',
    host='localhost',
    port=3306,
    user='root',
    passwd='931001',
    db='csb',
)
password="123456"
	
@app.route('/print/', methods=['GET', 'POST'])
def index():
	now = datetime.datetime.now()
	nowtime = now.strftime('%Y-%m-%d %H:%M:%S')
	if request.method != 'POST':
		return ""
	if 'password' not in request.form: 
		return ""
	if request.form['password']!=password:
		return ""
	if 'success' not in request.form:
		d = collections.OrderedDict()
		x=db.select('info', where="flag=0")
		if len(x)!=0:
			for key in x:
				d[key.msgid]=key.con
				db.insert("log",msgid=key.msgid,time=nowtime,state="send")
			return json.dumps(d)
		else:
			return ""
	else:
		msgid=request.form['success']
		if msgid.isdigit():
			try:
				db.update('info', where='msgid=$msgid',flag=1,vars=locals())
				db.insert("log",msgid=msgid,time=nowtime,state="receive")
			except:
				pass
		return ""

if __name__ == '__main__':
	app.run(debug=True,use_debugger=True,host='0.0.0.0',port=3000)

