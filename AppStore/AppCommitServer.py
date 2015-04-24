#encoding=utf-8
from __future__ import unicode_literals
import __init__ # 主要为了在没有加入到环境变量时，可以引用父目录的文件
import sys
import os
import platform
import time
import json
import subprocess
import BaseHTTPServer  
import urlparse
import urllib

import MySQLdb

import logutil

def _info(message):
    _logger = logutil.getLogger("CommitServer")
    _logger.info(message)

def _debug(message):
    _logger = logutil.getLogger("CommitServer")
    _logger.debug(message)

_commit_file_cache_dir = None
  
class WebRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):  
    def do_GET(self):  
        """ 
        """  
        parsed_path = urlparse.urlparse(self.path)  
        message_parts = [  
                'CLIENT VALUES:',  
                'client_address=%s (%s)' % (self.client_address,  
                                            self.address_string()),  
                'command=%s' % self.command,  
                'path=%s' % self.path,  
                'real path=%s' % parsed_path.path,  
                'query=%s' % parsed_path.query,  
                'request_version=%s' % self.request_version,  
                '',  
                'SERVER VALUES:',  
                'server_version=%s' % self.server_version,  
                'sys_version=%s' % self.sys_version,  
                'protocol_version=%s' % self.protocol_version,  
                '',  
                'HEADERS RECEIVED:',  
                ]

        _info("%s %s %s"%(self.command, self.path, self.request_version))
        for name, value in sorted(self.headers.items()):  
            message_parts.append('%s=%s' % (name, value.rstrip()))  
        message_parts.append('')  
        message = '\r\n'.join(message_parts)  
        self.send_response(200)  
        self.end_headers()

        # _info(message_parts)
        self.wfile.write(message)

        try:
            self.doAction()
        except Exception, e:
            _info("doAction Exception:"+str(e))

        # deinitMysql()

    def doAction(self):
        global _commit_file_cache_dir

        parsed_path = urlparse.urlparse(self.path)
        action = parsed_path.path

        # commitWithFile?file=/a/b/c
        if action == "/commitWithFile":
            querys = parsed_path.query.split("&")
            for query in querys:
                key, value = query.split("=")
                if key.lower() == "file":
                    filepath = urllib.unquote(value)
                    _info("=== Commit with file %s begin ==="%filepath)

                    # 初始化数据库连接
                    initMysql()

                    filename = "%s_%s"%(time.strftime("%Y_%m_%d_%H_%M_%S"), os.path.basename(filepath))
                    targetCachePath = os.path.join(_commit_file_cache_dir, filename)
                    os.rename(filepath, targetCachePath)
                    _info("=== Remove to %s ===="%targetCachePath)

                    fp = open(targetCachePath, "r")
                    commit(fp.read())
                    fp.close()

                    _info("=== Commit with file %s end ==="%targetCachePath)
                    break


_mysqlConn = None
_mysqlCur = None
def initMysql():
    global _mysqlCur, _mysqlConn

    if _mysqlConn is not None:
        _mysqlConn.ping()

        if _mysqlCur is not None:
            try:
                _mysqlCur.close()
            except Exception, e:
                pass
        _mysqlCur = _mysqlConn.cursor()
        return

    # 初始化数据库 开始
    MYSQL_HOST     = "jiangerji.mysql.rds.aliyuncs.com"
    MYSQL_PASSPORT = "jiangerji"
    MYSQL_PASSWORD = "eMBWzH5SIFJw5I4c"
    MYSQL_DATABASE = "spider"

    if platform.system() == 'Windows':
        MYSQL_HOST="localhost"
        MYSQL_PASSPORT="root"
        MYSQL_PASSWORD="123456"
        MYSQL_DATABASE="spider"

    _mysqlConn=MySQLdb.connect(host=MYSQL_HOST, user=MYSQL_PASSPORT, passwd=MYSQL_PASSWORD, db=MYSQL_DATABASE, charset="utf8")
    _info("Connect to %s:%s"%(MYSQL_HOST, MYSQL_DATABASE))
    _mysqlCur = _mysqlConn.cursor()
    # 初始化数据库 结束

def deinitMysql():
    global _mysqlCur, _mysqlConn

    if _mysqlConn != None:
            _mysqlConn.commit()

    if _mysqlCur != None:
        _mysqlCur.close()

    if _mysqlConn != None:
        _mysqlConn.close()

    _mysqlCur = None
    _mysqlConn = None


# 处理app
def _handleAppInfo(appInfo):
    global _mysqlCur, _mysqlConn

    trackid = appInfo.trackid
    schemesStr = ":".join(appInfo.schemes)

    #"""
    # 是否在数据库中
    cmd = "select scheme from appstores where trackid='%s';"%trackid
    _mysqlCur.execute(cmd)
    schemeResult = _mysqlCur.fetchone()
    if schemeResult is not None:
        # 已经在数据库中了，更新scheme
        schemeSrc = schemeResult[0]
        needUpdate = True
        schemeSrcList = set()
        if schemeSrc is not None and len(schemeSrc.strip()) > 0:
            schemeSrcList = set(schemeSrc.split(":"))
            if set(appInfo.schemes).issubset(schemeSrcList):
                needUpdate = False

        if needUpdate:
            _info("--- Update Scheme %s ---"%trackid)
            _info(appInfo)
            schemesStr = ":".join(list(schemeSrcList.union(set(appInfo.schemes))))
            _info("    scheme is "+schemesStr)
            cmd = 'update appstores set scheme="%s", version=-2 where trackid="%s";'%(schemesStr,  trackid)
            _mysqlCur.execute(cmd)
            _mysqlConn.commit()
            _info("--- Update Scheme %s Finish ---"%trackid)
        else:
            # _info("--- No need to update %s ---"%trackid)
            pass
    else:
        # 不在数据库中
        _info("--- New AppInfo %s ---"%trackid)
        _info("    scheme is "+schemesStr)

        # 获取bundle id
        # https://itunes.apple.com/lookup?id=414478124&country=cn
        url = "https://itunes.apple.com/lookup?id=%s"%trackid
        if True:
            url += "&country=cn"

        cacheDir = os.path.join(_rootDir, "cache")
        cacheDir = os.path.join(cacheDir, "appstores")
        cacheDir = os.path.join(cacheDir, "html")
        
        try:
            os.makedirs(cacheDir)
        except Exception, e:
            pass

        cacheFile = os.path.join(cacheDir, "app_%s.html"%trackid)
        try:
            appInfoJson = json.loads(_getUrlContent(url, cacheFile, jsEnable=False))
            results = appInfoJson.get("results")
            appInfo.setAppInfo(results[0])
        except Exception, e:
            _info("--- Get price exception:"+str(e)+" ---")
            os.remove(cacheFile)

        _info(appInfo)
        icon60 = appInfo.icon60
        icon512 = appInfo.icon512
        try:
            icons = _getAppIcon(trackid)
            if icons is not None:
                icon60, icon512 = icons
        except Exception, e:
            pass

        cmd = 'insert into appstores (trackid, name, scheme, icon60, icon512, addtime, version, price, bundleid, trackurl, ipadonly) values ' + '("%s","%s","%s","%s","%s","%s",-2,"%s","%s","%s", %d)'%(trackid, appInfo.name, schemesStr, icon60, icon512, time.strftime("%Y_%m_%d_%H"), str(appInfo.price), appInfo.bundleId, appInfo.trackViewUrl, appInfo.ipadOnly : 1 ? 0)
        _mysqlCur.execute(cmd)
        _mysqlConn.commit()
        _info("--- New AppInfo %s Finish ---"%trackid)
    #"""

def _getUrlContent(url, cacheFile, jsEnable=True):
    target_path = cacheFile

    if not os.path.isfile(target_path):
        if not jsEnable:
            wget = 'wget --user-agent="Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)"'
            command = wget + ' "%s" -O %s --timeout=60 --tries=2'%(url, target_path)
        else:
            load_web_page_js_dir = os.path.realpath(os.path.join(_rootDir, "bin"))
            load_web_page_js = os.path.realpath(os.path.join(load_web_page_js_dir, "loadAnnie.js"))
            command = 'phantomjs --load-images=false "%s" "%s" "%s"'%(load_web_page_js, url, target_path)
        _info(command)

        out = "1output.txt"
        outfp = open(out, "a+")
        errfp = open("1error.txt", "a+")
        try:
            p = subprocess.Popen(command, shell=True, stdout=outfp, stderr=errfp)
            
            state = p.wait()
            
            _info("Load Annie page state:%d"%state)
        except Exception, e:
            _info("subprocess exception:"+str(e))

    return open(target_path).read()

def _getAppIcon(trackid):
    from lxml import etree

    if trackid is None:
        return None

    url = "https://itunes.apple.com/cn/app/id%s?mt=8"%trackid
    cacheDir = os.path.join(_rootDir, "cache")
    cacheDir = os.path.join(cacheDir, "appstores")
    cacheDir = os.path.join(cacheDir, "html")
    
    try:
        os.makedirs(cacheDir)
    except Exception, e:
        pass

    cacheFile = os.path.join(cacheDir, "itunes_%s.html"%trackid)
    content = None
    try:
        content = _getUrlContent(url, cacheFile)
        doc = etree.HTML(content)

        rows = doc.xpath("//div[@id='left-stack']//img[@class='artwork']")
        for row in rows:
            icon60 = row.get("src")
            icon512 = row.get("src-swap-high-dpi")

            return (icon60, icon512)
    except Exception, e:
        _info("get url content exception:"+str(e))

    try:
        os.remove(cacheFile)
        _info("remove:"+cacheFile)
    except Exception, e:
        _info("remove:"+e)
    
    return None

def commit(content):
    appInfos = json.loads(content)
    # _info(content)

    trackids = appInfos.keys()
    for trackid in trackids:
        schemes = appInfos.get(trackid).get("schemes", None)
        name = appInfos.get(trackid).get("name", None)
        price = appInfos.get(trackid).get("price", 0)
        bundleId = appInfos.get(trackid).get("bundleId", None)
        trackViewUrl = appInfos.get(trackid).get("trackViewUrl", None)

        appInfo = _AppInfo(trackid, name, schemes, price, bundleId, trackViewUrl)

        _handleAppInfo(appInfo)

    _mysqlConn.commit()
    # _mysqlCur.close()
    # _mysqlConn.close()

class _AppInfo():
    def __init__(self, trackid, name, schemes, price, bundleId, trackViewUrl):
        self.trackid = trackid
        self.name = name
        # schemes is a list
        self.schemes = schemes

        self.price = price
        self.bundleId = bundleId
        self.trackViewUrl = trackViewUrl

        self.icon60 = None
        self.icon512 = None

    def setAppInfo(self, info):
        self.price = info.get("price", "0")
        self.bundleId = info.get("bundleId", None)
        self.trackViewUrl = info.get("trackViewUrl", None)
        self.icon60 = info.get("artworkUrl60", None)
        self.icon512 = info.get("artworkUrl512", None)

    def __str__(self):
        result = ["AppInfo:"]
        result.append("%9s: %s"%("trackid", self.trackid))
        result.append("%9s: %s"%("name", self.name))
        result.append("%9s: %s"%("schemes", self.schemes))
        result.append("%9s: %s"%("price", self.price))
        result.append("%9s: %s"%("bundleId", self.bundleId))
        result.append("%9s: %s"%("trackViewUrl", self.trackViewUrl))
        result.append("%9s: %s"%("icon60", self.icon60))
        result.append("%9s: %s"%("icon512", self.icon512))

        return "\n".join(result)

def main(port=9156):
    server = BaseHTTPServer.HTTPServer(('127.0.0.1', 9156), WebRequestHandler)  
    server.serve_forever()  

_rootDir = "."

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')

    _rootDir = os.path.dirname(os.path.realpath(sys.argv[0]))
    _rootDir = os.path.dirname(_rootDir)
    os.chdir(_rootDir) # 保证spider cache目录一致

    _commit_file_cache_dir = os.path.join(".", "AppStore")
    _commit_file_cache_dir = os.path.join(_commit_file_cache_dir, "scheme")
    _commit_file_cache_dir = os.path.join(_commit_file_cache_dir, "commit")
    try:
        os.makedirs(_commit_file_cache_dir)
    except Exception, e:
        pass

    port = 9156
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except Exception, e:
            pass

    _info("=== Start server at 127.0.0.1:%d"%port)
    _info(str(os.environ))
    main(port)
