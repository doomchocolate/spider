#encoding=utf-8
from __future__ import unicode_literals
import __init__ # 主要为了在没有加入到环境变量时，可以引用父目录的文件
import sys
import os
import platform
import time
import json
import re
from lxml import etree

# 第三方依赖库
import MySQLdb
import logutil
from AppClass import AppInfo
import AppStoreConstants
import CommonUtils

def _info(message):
    _logger = logutil.getLogger("CheckIpadOnly")
    _logger.info(message)


def main(filepath=None, indent=False):
    mysqlConn = None
    mysqlCur  = None

    host    = AppStoreConstants.MYSQL_HOST
    user    = AppStoreConstants.MYSQL_PASSPORT
    passwd  = AppStoreConstants.MYSQL_PASSWORD
    db      = AppStoreConstants.MYSQL_DATABASE

    _info("=== Start Main ===")
    try:
        mysqlConn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, charset="utf8")
        mysqlCur  = mysqlConn.cursor()
        _info("Connect to %s@%s"%(host, user))
    except MySQLdb.Error,e:
        _info("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        return

    cmd = 'select trackid from appstores where ipadonly=-1;'
    mysqlCur.execute(cmd)

    results = mysqlCur.fetchall()

    updateFormat = 'update appstores set ipadonly=%d where trackid=%s;'
    for app in results:
        try:
            trackid = app[0]
            appInfo = getAppIcon(trackid)

            print "%10s %s"%(trackid, appInfo.ipadOnly)
            ipadOnly = 0
            if appInfo.ipadOnly:
                ipadOnly = 1
            cmd = updateFormat%(ipadOnly, trackid)
            mysqlCur.execute(cmd)
        except Exception, e:
            print "Exception:", trackid, str(e)

    mysqlConn.commit()
    mysqlCur.close()
    mysqlConn.close()

def requestUrlContent(url, cache_dir=None, filename=None):
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

    if (not os.path.isfile(target_path)):
        state = os.system(command.encode("utf-8")) # 在windows下是gb2312, 在ubuntu主机上应该是utf-8
        if state != 0:
            print url, "download failed!"
    else:
        pass

    # 需要保证返回的字符串是ascii编码，否则lxml xpath解析可能会出问题
    # phantomjs保存的文件是utf-8编码，所以需要进行转码为ascii编码
    return open(target_path).read()

def getAppIcon(trackid, isCn=True):
    appInfo = None

    htmlCacheDir = "./cache/appstores/html"

    try:
        url = "https://itunes.apple.com/lookup?id=%s"%trackid
        if isCn:
            url += "&country=cn"
        appInfoJson = json.loads(requestUrlContent(url, htmlCacheDir, "app_%s.html"%trackid))
        results = appInfoJson.get("results")
        
        if len(results) > 0:
            appInfo = AppInfo()
            appInfo.setAppInfo(results[0])
    except Exception, e:
        print "get trackid except:", e

    if appInfo is None:
        try:
            os.remove(os.path.join(htmlCacheDir, "app_%s.html"%trackid))
        except Exception, e:
            pass

    return appInfo


if __name__=="__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')

    workDir = os.path.dirname(os.path.realpath(sys.argv[0]))
    os.chdir(os.path.dirname(workDir)) # 保证spider cache目录一致

    oldStdout = sys.stdout
    logFile = CommonUtils.openLogFile(mode="w")

    if logFile is not None:
        sys.stdout = logFile

    print "============================================"
    print "change work direcotory to workDir", workDir
    print "Start AppStore Spider:", time.asctime()

    main()

    if oldStdout:  
        sys.stdout = oldStdout

    if logFile is not None:
        logFile.close()