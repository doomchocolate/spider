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

_logger = None

def _info(message):
    if _logger:
        _logger.info(message)

def _debug(message):
    if _logger:
        _logger.debug(message)
  
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
            pass
        except Exception, e:
            raise e

    def doAction(self):
        parsed_path = urlparse.urlparse(self.path)
        action = parsed_path.path

        # commitWithFile?file=/a/b/c
        if action == "/commitWithFile":
            querys = parsed_path.query.split("&")
            for query in querys:
                key, value = query.split("=")
                if key.lower() == "file":
                    filepath = urllib.unquote(value)
                    _info("=== Commit with file %s ==="%filepath)

                    fp = open(filepath, "r")
                    commit(fp.read())
                    fp.close()

_mysqlConn = None
_mysqlCur = None
def initMysql():
    global _mysqlCur, _mysqlConn
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
        _info(appInfo)
        icon60 = None
        icon512 = None
        try:
            icons = _getAppIcon(trackid)
            if icons is not None:
                icon60, icon512 = icons
        except Exception, e:
            pass

        cmd = 'insert into appstores (trackid, name, scheme, icon60, icon512, addtime, version) values ' + '("%s","%s","%s","%s","%s","%s",-2)'%(trackid, appInfo.name, schemesStr, icon60, icon512, time.strftime("%Y_%m_%d_%H"))
        _mysqlCur.execute(cmd)
        _mysqlConn.commit()
        _info("--- New AppInfo %s Finish ---"%trackid)
    #"""

def _getUrlContent(url, cacheFile):
    target_path = cacheFile

    if not os.path.isfile(target_path) or True:
        load_web_page_js_dir = os.path.realpath(os.path.join(_rootDir, "bin"))
        load_web_page_js = os.path.realpath(os.path.join(load_web_page_js_dir, "loadAnnie.js"))
        command = 'phantomjs --load-images=false "%s" "%s" "%s"'%(load_web_page_js, url, target_path)
        _info(command)

        out = "1output.txt"
        outfp = open(out, "a+")
        errfp = open("1error.txt", "a+")
        try:
            p = subprocess.Popen(command, shell=True, stdout=outfp, stderr=errfp)
            # fp = open("geturl.txt", "w")
            # fp.write("##### start #####\n")

            # while p.poll() == None:
            #     line = p.stdout.readline()
            #     line += p.stderr.readline()
            #     if len(line) > 0:
            #         fp.write(line)
            state = p.wait()
            # line = p.stdout.read()
            # line += p.stderr.read()
            # fp.write(line)
            # fp.write("\n##### end #####\n")
            _info("Load Annie page state:%d"%state)
        except Exception, e:
            _info("subprocess exception:"+str(e))

        # state = os.system(command.encode("utf-8"))

    return open(target_path).read()

def _getAppIcon(trackid):
    from lxml import etree

    if trackid is None:
        return None

    url = "https://itunes.apple.com/cn/app/id%s?mt=8"%trackid
    cacheDir = os.path.join(_rootDir, "cache")
    cacheDir = os.path.join(cacheDir, "itunes")
    
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
        print "get url content exception:", e

    try:
        os.remove(cacheFile)
        _info("remove:"+cacheFile)
    except Exception, e:
        _info("remove:"+e)
    
    return None

def commit(content):
    appInfos = json.loads(content)
    _info(content)

    trackids = appInfos.keys()
    for trackid in trackids:
        schemes = appInfos.get(trackid).get("schemes", None)
        name = appInfos.get(trackid).get("name", None)
        appInfo = _AppInfo(trackid, name, schemes)

        _handleAppInfo(appInfo)

    _mysqlConn.commit()
    # _mysqlCur.close()
    # _mysqlConn.close()

class _AppInfo():
    def __init__(self, trackid, name, schemes):
        self.trackid = trackid
        self.name = name
        # schemes is a list
        self.schemes = schemes

    def __str__(self):
        result = ["AppInfo:"]
        result.append("%9s: %s"%("trackid", self.trackid))
        result.append("%9s: %s"%("name", self.name))
        result.append("%9s: %s"%("schemes", self.schemes))

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

    _logger = logutil.getLogger("CommitServer")

    # 初始化数据库连接
    initMysql()

    port = 9156
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except Exception, e:
            pass

    _info("=== Start server at 127.0.0.1:%d"%port)
    main(port)