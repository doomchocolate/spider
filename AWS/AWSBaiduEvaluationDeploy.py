#encoding=utf-8
from __future__ import unicode_literals
import __init__ # 主要为了在没有加入到环境变量时，可以引用父目录的文件
import sys
import os
import time
import platform

import CommonUtils

from Base.BaseDeploy import BaseDeploy
import AWSConstants

class AWSBaiduEvaluationDeploy(BaseDeploy):
    
    def __init__(self):
        host=AWSConstants.MYSQL_HOST
        user=AWSConstants.MYSQL_PASSPORT
        passwd=AWSConstants.MYSQL_PASSWORD
        db=AWSConstants.MYSQL_DATABASE

        if platform.system() == 'Windows':
            host="localhost"
            user="root"
            passwd="123456"
            db="test"

        BaseDeploy.__init__(self, host, user, passwd, db)

    def start(self):
        contents = self.getContents("evaluations")
        print len(contents)
        for i in contents:
            (_id, evaluationId, productId, createTime, title, content, thumbnails, deploy_status) = i


    

def main():
    deploy = AWSBaiduEvaluationDeploy()
    deploy.start()

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')

    workDir = os.path.dirname(os.path.realpath(sys.argv[0]))
    os.chdir(os.path.dirname(workDir))

    logFile = CommonUtils.openLogFile()

    oldStdout = sys.stdout  
    sys.stdout = logFile

    print "============================================"
    print "change work direcotory to workDir", workDir
    print "Start AWS Baidu Evaluation Deploy:", time.asctime()

    main()

    logFile.close()  
    if oldStdout:  
        sys.stdout = oldStdout