#encoding=utf-8
from __future__ import unicode_literals
import __init__ # 主要为了在没有加入到环境变量时，可以引用父目录的文件
import sys
import os
import time
import platform
import tempfile
import re

# 第三方依赖库
import MySQLdb

# 自身工程库
import CommonUtils
import Constants

PIC_SUFFIX = ["png", "jpg", "gif", "jpeg", "bmp"] # 图片文件后缀

class BaseSpider:

    def __init__(self, _createTableCommand, host=Constants.MYSQL_HOST, user=Constants.MYSQL_PASSPORT, passwd=Constants.MYSQL_PASSWORD, db=Constants.MYSQL_DATABASE, charset="utf8"):
        self._host = host
        self._user = user
        self._passwd = passwd
        self._db = db
        self._charset = charset

        # 连接数据库
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

        # 创建mysql table 
        self.mysqlCur.execute(_createTableCommand)
        self.mysqlConn.commit()

        self.totalSuccCount = 0
        self.flushCount = 0

        self.valueTable = {} # 主要用于缓存isInTable的数据

    # 获取url的内容, 如果是图片，返回图片的地址
    # 如果js_enable为True, 则使用phantomjs进行获取网页地址
    def requestUrlContent(self, url, cache_dir=None, filename=None, js_enable=False, force_update=False):
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

        wget = 'wget --user-agent="Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)"'
        command = wget + ' "%s" -O %s --timeout=60 --tries=2'%(url, target_path)

        if js_enable:
            load_web_page_js_dir = os.path.join(".", "bin")
            load_web_page_js = os.path.join(load_web_page_js_dir, "load.js")
            # load_web_page_js = load_web_page_js.replace("\\", "/")
            command = 'phantomjs --load-images=false "%s" "%s" "%s"'%(load_web_page_js, url, target_path)

        # print "current dir", os.path.realpath(os.curdir)
        # print "Request Url:", command.encode("utf-8")
        if (not os.path.isfile(target_path)) or force_update:
            state = os.system(command.encode("utf-8")) # 在windows下是gb2312, 在ubuntu主机上应该是utf-8
            print url, "download successful!"
        else:
            # print url, "is already downloaded!"
            pass

        if ext[1:].lower() in PIC_SUFFIX:
            return target_path

        # 需要保证返回的字符串是ascii编码，否则lxml xpath解析可能会出问题
        # phantomjs保存的文件是utf-8编码，所以需要进行转码为ascii编码
        if js_enable:
            return open(target_path).read().decode("utf8").encode("gb18030")
        else:
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
        # _key = tableName + key
        # valueTable = str(value)
        # if self.valueTable.has_key(_key):
        #     if value in self.valueTable[_key]:
        #         return True
        #     else:
        #         return False

        # command = 'select `%s` from `%s`'%(key, tableName)
        # try:
        #     self.mysqlCur.execute(command)
        #     self.valueTable[_key] = map(lambda x: x[0], self.mysqlCur.fetchall())
        #     self.valueTable[_key] = map(str, self.valueTable[_key])
        #     if value in self.valueTable[_key]:
        #         return True
        # except Exception, e:
        #     print e
        
        # return False

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

    def reMatch(self, content, pattern):
        pattern = re.compile(pattern)

        result = ""
        match = re.search(pattern, content)
        if match:
            result = match.group()
            try:
                result = unicode(result, "utf-8")
            except Exception, e:
                pass

        return result

    def reFindall(self, content, pattern):
        pattern = re.compile(pattern)
        match = re.findall(pattern, content)

        return match

    def clearTable(self, table_name):
        if self.mysqlConn is not None:
            try:
                self.mysqlCur.execute("TRUNCATE `%s`;"%table_name)
                self.mysqlConn.commit()
            except Exception, e:
                print "clear table exception:", e

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
