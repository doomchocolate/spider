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

class AWSBaiduEvaluationDeploy(BaseDeploy):

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
        tableName = "evaluations"

        allEvaluations = self.getContents(tableName)
        succCount = 0
        failedList = []

        for evaluation in allEvaluations:
            _id = evaluation[0]
            newsId = evaluation[1]
            productId = evaluation[2]
            createTime = evaluation[3]
            title = evaluation[4]
            try:
                title = title[title.index("-")+1:]
            except Exception, e:
                pass
            intro = "" # 从products表中获取
            try:
                intro = self.getValue("products", "product_intro", "product_id", productId, 1)[0]
            except Exception, e:
                pass
            
            print intro
            detail = evaluation[5]
            thumbnail = None
            try:
                thumbnail = eval(evaluation[6])[0]
            except Exception, e:
                pass
            buyUrl = "" # 从products表中获取
            try:
                buyUrl = self.getValue("products", "buy_url", "product_id", productId, 1)[0]
            except Exception, e:
                pass

            article = AWSArticle(tableName, newsId, title, intro, detail, thumbnail, self._articleCur, catId=15, buyUrl=buyUrl, createTime=createTime)
            article.addFlag(AWSArticle.ARTICLE_DISABLE_TAGS)
            if article.deploy():
                print "发布成功:"
                print article
                self.update(tableName, _id, "deploy_status", 1)
                self.commit() # 提交一次
                succCount += 1
            else:
                print "发布失败", newsId, title
                failedList.append(article)

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

    deploy = AWSBaiduEvaluationDeploy(host, user, passwd, db)
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