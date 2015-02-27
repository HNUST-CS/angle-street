import sys
sys.path.append('/home/bae/app/deps')
from IPython import start_ipython
start_ipython()

 
def check():
    for i in Admin.objects: i.validate()
    for i in Shop.objects: i.validate()
    for i in Order.objects: i.validate()
    for i in WeixinQueue.objects: i.validate()
    for i in Log.objects: i.validate()
    for i in User.objects: i.validate()
    for i in PrintQueue.objects: i.validate()
