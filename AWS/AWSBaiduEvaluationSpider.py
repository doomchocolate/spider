#encoding=utf-8
from __future__ import unicode_literals
import __init__ # 主要为了在没有加入到环境变量时，可以引用父目录的文件
import sys
import os
import platform
import time

import AWSConstants
import CommonUtils

from Baidu.BaiduEvaluationSpider import BaiduEvaluationSpider

def main():
    host=AWSConstants.MYSQL_HOST
    user=AWSConstants.MYSQL_PASSPORT
    passwd=AWSConstants.MYSQL_PASSWORD
    db=AWSConstants.MYSQL_DATABASE

    if platform.system() == 'Windows':
        host="localhost"
        user="root"
        passwd="123456"
        db="test"

    spider = BaiduEvaluationSpider(host, user, passwd, db)
    spider.start()

if __name__=="__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')

    workDir = os.path.dirname(os.path.realpath(sys.argv[0]))
    os.chdir(os.path.dirname(workDir)) # 保证spider cache目录一致

    logFile = CommonUtils.openLogFile()

    oldStdout = sys.stdout  
    sys.stdout = logFile

    print "============================================"
    print "change work direcotory to workDir", workDir
    print "Start AWS Baidu Evaluation Spider:", time.asctime()

    main()

    logFile.close()  
    if oldStdout:  
        sys.stdout = oldStdout