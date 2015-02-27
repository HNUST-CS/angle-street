#coding=utf8
from flask import Flask  
import urllib,urllib2
import random
import json
import win32ui
import win32print
import win32con
import time
import thread
import threading
import datetime
import os
import shutil
from collections import OrderedDict
from Tkinter import *
class timer(threading.Thread):
    def __init__(self, url, password, interval):  
        threading.Thread.__init__(self)  
        self.thread_url = url
        self.thread_num = password
        self.interval = interval
        self.thread_stop = False
    def run(self):
        while not self.thread_stop:  
            now = datetime.datetime.now()
            filename = now.strftime('%Y-%m-%d')
            nowtime = now.strftime('%Y-%m-%d %H:%M:%S')
            re=""
            try:
                req = urllib2.Request(self.thread_url,"password="+self.thread_num)
                response = urllib2.urlopen(req)
                re = response.read()
            except:
                pass
            if(re!=""):
                d=""
                try:
                    d=json.loads(re,object_pairs_hook=OrderedDict)
                except:
                    pass
                if type(d) is not OrderedDict:
                    pass
                else:
                    for key in d:
                        queue.append((key,d[key]))
                    while(len(queue)!=0):
                        content=queue.pop(0)
                        try:
                            
                            try:
                                req = urllib2.Request(self.thread_url,"success="+content[0]+"&password="+self.thread_num)
                                response = urllib2.urlopen(req)
                                fp = open(filename + ".txt" , "a" )
                                fp.write(nowtime + " id:" + content[0] + " successful\n")
                                fp.close()
                                lb.insert(END,nowtime + " id:" + content[0] + " successful")
                            except:
                                fp = open(filename + ".txt","a")
                                fp.write(nowtime + " " + content[0] + " send failed\n")
                                fp.close()
                                lb.insert(END,nowtime + " id:" + content[0] + " send failed")
                        except:
                            fp = open(filename + ".txt","a")
                            fp.write(nowtime + " " + content[0] + " print failed\n")
                            fp.close()
                            lb.insert(END,nowtime + " id:" + content[0] + " print failed")
            else:
                pass
            time.sleep(self.interval)
    def stop(self):
        self.thread_stop = True
def begin():
    root.title("begin...")
    try:
        thread1.start()
    except:
        pass
def end():
    root.title("end...")
    thread1.stop()

thread1 = timer("http://127.0.0.1:5000/print/","123456", 5)
queue=[]

root = Tk()
root.minsize(300,600)
root.maxsize(300,600)
root.title(u"Hello")
Button(root,text = u'begin',command = begin,width = 8,height = 1).place(x = 90,y = 20,anchor = N)
Button(root,text = u'end',command = end,width = 8,height = 1).place(x = 200,y = 20,anchor = N)
lb = Listbox(root,width = 25,height = 50)
sl = Scrollbar(root)
sl.place(x=295,y=329,height=517,anchor = E)
lb['yscrollcommand'] = sl.set
sl['command'] = lb.yview
lb.place(x=1,y=70,height = 518,width=276,anchor = NW)
mainloop()
try:
    if thread1.isAlive():
        thread1.stop()
except:
    pass