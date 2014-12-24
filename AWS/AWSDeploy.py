#encoding=utf-8
from __future__ import unicode_literals
import __init__ # 主要为了在没有加入到环境变量时，可以引用父目录的文件
import sys
import os
import platform
import time
import datetime

import CommonUtils

# from AWSBaiduNewsSpider import AWSBaiduNewsSpider
# from AWSBaiduNewsDeploy import AWSBaiduNewsDeploy

def main():
    commands = ["News", "Product", "Evaluation"]

    for command in commands:
        spiderCommand = 'python AWS/AWSBaidu%sSpider.py'%command
        try:
            print "开始更新抓取", command, datetime.datetime.now()
            state = os.system(spiderCommand)
            print "完成更新抓取", command, state, datetime.datetime.now()
        except Exception, e:
            print "  更新抓取", command, "异常", e
        print "\n"

        deployCommand = 'python AWS/AWSBaidu%sDeploy.py'%command
        try:
            print "开始部署更新", command, datetime.datetime.now()
            state = os.system(deployCommand)
            print "完成部署更新", command, state, datetime.datetime.now()
        except Exception, e:
            print "  部署更新", command, "异常", e
        print "\n"

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
    print "Start AWS Deploy:", time.asctime()

    main()

    logFile.close()  
    if oldStdout:  
        sys.stdout = oldStdout