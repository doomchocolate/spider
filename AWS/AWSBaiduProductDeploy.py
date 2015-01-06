#encoding=utf-8
from __future__ import unicode_literals
import __init__ # 主要为了在没有加入到环境变量时，可以引用父目录的文件
import sys
import os
import time
import platform

import MySQLdb

import CommonUtils
import AWSConstants
from AWSArticle import AWSArticle
from Base.BaseDeploy import BaseDeploy

class AWSBaiduProductDeploy(BaseDeploy):

    def __init__(self, host, user, passwd, db):
        BaseDeploy.__init__(self, host, user, passwd, db)
        self._connectArticleMysql()

    def _connectArticleMysql(self):
        # host="localhost"
        # user="debian-sys-maint"
        # passwd="eMBWzH5SIFJw5I4c"
        # db="future-store"
        host=AWSConstants.MYSQL_HOST
        user=AWSConstants.MYSQL_PASSPORT
        passwd=AWSConstants.MYSQL_PASSWORD
        db=AWSConstants.MYSQL_DATABASE

        if platform.system() == 'Windows':
            host="localhost"
            user="root"
            passwd="123456"
            db="test"

        self._articleConn = None
        self._articleCur = None
        try:
            self._articleConn=MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, charset="utf8")
            self._articleCur = self._articleConn.cursor()
        except MySQLdb.Error,e:
             print "Mysql Error %d: %s" % (e.args[0], e.args[1])
             exception = e

    def start(self):
        tableName = "products"

        allProducts = self.getContents(tableName)
        succCount = 0
        failedList = []

        for product in allProducts:
            _id = product[0]
            newsId = product[1]
            title = product[3]
            intro = product[4]
            detail = product[5]
            thumbnail = product[6]
            buyUrl = product[12]

            if len(thumbnail) == 0:
                try:
                    thumbnail = eval(product[11])[0]
                except Exception, e:
                    raise e

            article = AWSArticle(tableName, newsId, title, intro, detail, thumbnail, self._articleCur, catId=14, buyUrl=buyUrl)
            if article.deploy():
                print "发布成功:"
                print article
                self.update(tableName, _id, "deploy_status", 1)
                self.commit() # 提交一次
                succCount += 1
            else:
                print "发布失败", newsId, title
                failedList.append(news)

            # if succCount > 0:
            #     break

        if self._articleConn != None:
            self._articleConn.commit()

        if self._articleCur != None:
            self._articleCur.close()

        if self._articleConn != None:
            self._articleConn.close()

        self._articleCur = None
        self._articleConn = None

        print "成功发布", succCount, "篇"
        print "发布失败", len(failedList), "篇"


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

    deploy = AWSBaiduProductDeploy(host, user, passwd, db)
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
    print "Start AWS Baidu Product Deploy:", time.asctime()

    main()

    logFile.close()  
    if oldStdout:  
        sys.stdout = oldStdout