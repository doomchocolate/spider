#encoding=utf-8
# from __future__ import unicode_literals
import __init__ # 主要为了在没有加入到环境变量时，可以引用父目录的文件
import sys
import time
import json
import os

# 第三方依赖库
import MySQLdb
import logutil

_guideAppList = [
    (444934666, "QQ"),
    (414603431, "QQ音乐"),
    (414478124, "微信"),
    (350962117, "微博"),
    (427941017,  "YY - 视频直播互动社区"),
    (448165862, "陌陌"),
    (425349261, "网易新闻"),
    (393765873, "爱奇艺视频"),
    (458318329, "腾讯视频-最全电视剧综艺电影动漫"),
    (793077082, "刀塔传奇-50V50!全新团战模式"),
    (468623917, "百度音乐-集下载,铃声,MV,电台,K歌于一体的高品质音乐播放器"),
    (452186370, "百度地图(语音导航)-最全最准免费地图"),
    (461703208, "高德地图(最专业的手机地图)——特色语音导航"),
    (592331499, "美颜相机 - 把手机变成自拍神器！")
    ]

def _info(message):
    _logger = logutil.getLogger("GuidInstallApp")
    _logger.info(message)

MYSQL_HOST     = "jiangerji.mysql.rds.aliyuncs.com"
MYSQL_PASSPORT = "jiangerji"
MYSQL_PASSWORD = "eMBWzH5SIFJw5I4c"
MYSQL_DATABASE = "spider"

def init():
    mysqlConn = None
    mysqlCur  = None

    try:
        mysqlConn = MySQLdb.connect(host=MYSQL_HOST, user=MYSQL_PASSPORT, passwd=MYSQL_PASSWORD, db=MYSQL_DATABASE, charset="utf8")
        mysqlCur  = mysqlConn.cursor()
        _info("Connect to %s@%s"%(MYSQL_DATABASE, MYSQL_PASSPORT))
    except MySQLdb.Error,e:
        _info("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        return

    cmd = 'insert into guideinstallapp (trackid, name, timestamp) values ("%s", "%s", "%s")'

    for app in _guideAppList:
        trackid, name = app
        mysqlCur.execute(cmd%(trackid, name, time.strftime("%Y_%m_%d_%H")))

    mysqlConn.commit()

    mysqlCur.close()
    mysqlConn.close()
    _info("=== Finish! ===")

from ctypes import *
_libEnc = None
def enc(input):
    global _libEnc
    if _libEnc is None:
        soPath = os.path.join(os.getcwd(), 'myencrypt.so')
        _libEnc = cdll.LoadLibrary(soPath)

    if input is None or len(input) == 0:
        return ""
    inputLength = len(input)

    _libEnc._encrypt.restype = c_char_p  

    encResult = _libEnc._encrypt(create_string_buffer(input), inputLength)

    return encResult

def testEnc():
    a = "ed2k"
    print enc(a)
    # exit()

def main(filepath=None, indent=False):
    # testEnc()

    mysqlConn = None
    mysqlCur  = None

    _info("=== Start Main ===")

    try:
        mysqlConn = MySQLdb.connect(host=MYSQL_HOST, user=MYSQL_PASSPORT, passwd=MYSQL_PASSWORD, db=MYSQL_DATABASE, charset="utf8")
        mysqlCur  = mysqlConn.cursor()
        _info("Connect to %s@%s"%(MYSQL_DATABASE, MYSQL_PASSPORT))
    except MySQLdb.Error,e:
        _info("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        return

    cmd = 'select a.* from appstores a join guideinstallapp b on a.trackid = b.trackid;'
    
    mysqlCur.execute(cmd)
    result = mysqlCur.fetchall()

    jsonResult = {}
    for i in result:
        app = {}
        app["name"] = i[2]
        _info("scheme is "+i[3])
        a = i[3]
        _info(type(a))
        a = i[3].encode("utf-8")
        # a = "teiron2273"
        # a = ""
        # for j in i[3]:
        #     a += j

        _info(type(a))
        _info("j:"+a)
        app["scheme"] = enc(a)#enc(i[3])
        app["icon60"] = i[4]
        app["icon512"] = i[5]
        jsonResult[i[1]] = app

    _info("=== Json Value Begin ===")
    if indent:
        content = json.dumps(jsonResult, indent=2)
    else:
        content = json.dumps(jsonResult)

    if filepath is not None:
        try:
            open(filepath, "w").write(content)
        except Exception, e:
            _info("Write to target exception:"+str(e))

    _info(content)
    _info("=== Json Value End ===")

    _info("=== Finish Main ===")

if __name__=="__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')

    """
    python GuideInstallApp.py targetPath -f

    targetPath: the json output file path
    -f: format the json output
    """
    if len(sys.argv) < 2:
        exit()

    targetPath = sys.argv[1]
    targetPath = os.path.realpath(targetPath)
    _info("Target path is %s"%targetPath)

    indent = False
    if "-f" in sys.argv:
        indent = True

    targetFolder = os.path.dirname(targetPath)
    if not os.path.isdir(targetFolder):
        _info("Target Folder %s isn't exsites!"%targetFolder)
        try:
            os.makedirs(targetFolder)
        except Exception, e:
            _info("Make target folder failed!"+str(e))
            exit()

    main(targetPath, indent=indent)
