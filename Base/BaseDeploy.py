#encoding=utf-8
from __future__ import unicode_literals
import __init__ # 主要为了在没有加入到环境变量时，可以引用父目录的文件
import sys
import os
import tempfile

# 第三方依赖库
import MySQLdb

import Constants
import CommonUtils
import BaseInterface

class BaseDeploy(BaseInterface.BaseInterface):

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

    def getValue(self, tableName, columnName, keyColumn, keyColumnValue, limit=-1):
        return BaseInterface.BaseInterface.getValue(self, self.mysqlCur, tableName, columnName, keyColumn, keyColumnValue, limit=-1)

    def update(self, tableName, _id, columnName, columnValue):
        if self.mysqlCur != None:
            command = "update `%s` set `%s`='%s' where `id`='%s'"%(tableName, columnName, str(columnValue), str(_id))
            # print command
            try:
                self.mysqlCur.execute(command)
            except Exception, e:
                print e

    def commit(self):
        if self.mysqlConn != None:
            self.mysqlConn.commit()

    def finish(self):
        if self.mysqlConn != None:
            self.mysqlConn.commit()

        if self.mysqlCur != None:
            self.mysqlCur.close()

        if self.mysqlConn != None:
            self.mysqlConn.close()

        self.mysqlCur = None
        self.mysqlConn = None