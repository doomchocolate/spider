#encoding=utf-8
from __future__ import unicode_literals
import __init__ # 主要为了在没有加入到环境变量时，可以引用父目录的文件
import sys
import os
import time
import platform
import tempfile

# 第三方依赖库
import MySQLdb

# 自身工程库
import CommonUtils
import Constants

PIC_SUFFIX = ["png", "jpg", "gif", "jpeg", "bmp"] # 图片文件后缀

class BaseSpider:

    def __init__(self, _createTableCommand):
        # 连接数据库
        self.mysqlConn = None
        self.mysqlCur = None
        exception = None
        try:
            if platform.system() == 'Windows':
                self.mysqlConn=MySQLdb.connect(host="localhost",user="root", passwd="123456",db="test",charset="utf8")
            else:
                self.mysqlConn=MySQLdb.connect(host="localhost",user=Constants.MYSQL_PASSPORT,passwd=Constants.MYSQL_PASSWORD,db=Constants.MYSQL_DATABASE,charset="utf8")
            self.mysqlCur = self.mysqlConn.cursor()
        except MySQLdb.Error,e:
             print "Mysql Error %d: %s" % (e.args[0], e.args[1])
             exception = e

        if self.mysqlConn == None or self.mysqlCur == None:
            # 打开数据失败，
            raise exception

        # 创建mysql table 
        self.mysqlCur.execute(_createTableCommand)
        self.mysqlConn.commit()

        self.totalSuccCount = 0
        self.flushCount = 0

    # 获取url的内容, 如果是图片，返回图片的地址
    def requestUrlContent(self, url, cache_dir=None, filename=None):
        if cache_dir != None and not os.path.isdir(cache_dir):
            os.makedirs(cache_dir)

        ext = os.path.splitext(url)[-1]
        if filename == None:
            filename = CommonUtils.md5(url) + ext

        target_path = None
        if cache_dir == None:
            target_path = tempfile.mktemp()
        else:
            target_path = os.path.join(".", cache_dir)
            target_path = os.path.join(target_path, filename)

        if target_path == None:
            target_path = tempfile.mktemp()

        command = 'wget "%s" -O %s '%(url, target_path)
        print "Request Url:", command
        if not os.path.isfile(target_path):
            state = os.system(command.encode("utf-8")) # 在windows下是gb2312, 在ubuntu主机上应该是utf-8
        else:
            print url, "is already downloaded!"

        if ext[1:].lower() in PIC_SUFFIX:
            return target_path

        return open(target_path).read()


    def getTableCount(self, tableName):
        value = 0
        try:
            self.mysqlCur.execute("select count(*) from `%s`"%tableName)
            value = self.mysqlCur.fetchone()[0]
        except Exception, e:
            value = -1

        return value

    # 检查某个值是否已经存在
    def isInTable(self, tableName, key, value):
        command = 'select count(id) from `%s` where `%s`="%s"'%(tableName, key, str(value))
        inTable = False
        try:
            self.mysqlCur.execute(command)
            if self.mysqlCur.fetchone()[0] > 0:
                inTable = True
        except Exception, e:
            print e

        return inTable


    def insert(self, command, value):
        print "插入数据库"
        result = False
        try:
            result = self.mysqlCur.execute(command, value)
            self.totalSuccCount += 1

            if self.totalSuccCount %30 == 0:
                self.mysqlConn.commit()
        except Exception, e:
            print e
            pass

        return result

    def finish(self):
        if self.mysqlConn != None:
            self.mysqlConn.commit()

        if self.mysqlCur != None:
            self.mysqlCur.close()

        if self.mysqlConn != None:
            self.mysqlConn.close()

        self.mysqlCur = None
        self.mysqlConn = None

            


if __name__ == "__main__":
    if len(sys.argv) == 1:
        exit(1)

    reload(sys)
    sys.setdefaultencoding('utf-8')

    workDir = os.path.dirname(os.path.realpath(sys.argv[0]))
    os.chdir(workDir)

    logFile = CommonUtils.openLogFile()

    oldStdout = sys.stdout  
    sys.stdout = logFile

    print "============================================"
    print "change work direcotory to workDir", workDir
    print "Start ArticleUtils:", time.asctime()

    logFile.close()  
    if oldStdout:  
        sys.stdout = oldStdout
