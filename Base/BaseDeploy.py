#encoding=utf-8
from __future__ import unicode_literals
import __init__ # 主要为了在没有加入到环境变量时，可以引用父目录的文件
import sys

# 第三方依赖库
import MySQLdb

import Constants

class BaseDeploy:

    def __init__(self, host=Constants.MYSQL_HOST, user=Constants.MYSQL_PASSPORT, passwd=Constants.MYSQL_PASSWORD, db=Constants.MYSQL_DATABASE, charset="utf8"):
        self.mysqlConn = None
        self.mysqlCur = None
        exception = None
        try:
            self.mysqlConn=MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, charset=charset)
            self.mysqlCur = self.mysqlConn.cursor()
        except MySQLdb.Error,e:
             print "Mysql Error %d: %s" % (e.args[0], e.args[1])
             exception = e

        if self.mysqlConn == None or self.mysqlCur == None:
            # 打开数据失败，
            raise exception

    def getContents(self, tableName):
        result = []

        try:
            command = "select * from %s where deploy_status=0"%tableName
            self.mysqlCur.execute(command)
            result = self.mysqlCur.fetchall()
        except Exception, e:
            print e

        return result