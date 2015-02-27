#coding=utf8

import requests
import json
import time
service_url = 'http://localhost:3000/api/admin/print/task'
key = "wasd"


import logging
         
hdlr = logging.FileHandler('log.txt')
hdlr.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger = logging.getLogger()
logger.addHandler(hdlr)
logger.setLevel(logging.NOTSET)
logger.info('start run')






import win32ui
import win32print
import win32con

def printContent(raw_data):
    try:
        printer_name = win32print.GetDefaultPrinter ()
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            hJob = win32print.StartDocPrinter (hPrinter, 1, ("test of raw data", None, "RAW"))
            try:
                win32print.StartPagePrinter (hPrinter)
                win32print.WritePrinter (hPrinter, raw_data.encode("gbk"))
                win32print.EndPagePrinter (hPrinter)
            finally:
                win32print.EndDocPrinter (hPrinter)
        finally:
            win32print.ClosePrinter (hPrinter)
    except Exception as e: 
        logger.error("printContent error "+e)
    return True

def mainloop():
    ok = []
    while 1:
        try:
            task = requests.post(service_url, {'data':json.dumps({"key":key, "okid":ok, }) } ).content
            logger.info("get task from service \n %s\n"%str(task))
            ok = []
            for i in json.loads(task):
                id = i['_id']['$oid']
                content =  i['content']
                state = printContent(content)
                if state :
                    ok.append(id)
                    logger.info("print %s \n %s\n\n"%(id,content))
                else:
                    logger.error("print %s \n %s\n\n"%(id,content))
        except Exception as e:
            logger.error(str(e))
            time.sleep(10)
            continue
        time.sleep(5)
mainloop()


