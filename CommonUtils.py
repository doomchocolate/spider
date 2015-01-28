#encoding=utf-8
from __future__ import unicode_literals
import sys
import os
import time
import codecs
import hashlib

"""
在log目录下创建filename.创建日期.log的日志文件
如果为None, filename默认为调用该接口的python文件名
"""
def openLogFile(filename=None, mode="a+"):
    if filename == None:
        filename = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    currentDate = time.strftime("%Y-%m-%d",time.localtime()) 

    filename += "-" + currentDate + ".log"

    logDir = "log"
    if not os.path.isdir(logDir):
        os.makedirs(logDir)

    return codecs.open("log"+os.path.sep+filename, mode, "utf-8")

def md5(source):
    result = hashlib.md5(source.encode('utf-8')).hexdigest()
    return result