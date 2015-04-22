#encoding=utf-8
from __future__ import unicode_literals
import __init__ # 主要为了在没有加入到环境变量时，可以引用父目录的文件
import sys
import time
import json
import os

# 第三方依赖库
import MySQLdb
import logutil
from AppClass import AppInfo

def _info(message):
    _logger = logutil.getLogger("GenerateAppSchemes")
    _logger.info(message)
    # print message

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

def _encrypt(input):
    # return input
    return enc(input)

def _generate(mysqlConn, mysqlCur, indent=False):
    # 获取最大版本号
    cmd = 'select max(version) from appstores where version > 0;'
    mysqlCur.execute(cmd)
    maxVersion = mysqlCur.fetchone()[0]
    _info("当前最大版本号: %s"%str(maxVersion))

    # 判断是否更新的scheme
    cmd = 'select count(id) from appstores where scheme is not null and version < 0;'
    mysqlCur.execute(cmd)
    needUpdate = mysqlCur.fetchone()[0] > 0
    _info("当前需要更新:"+str(needUpdate))

    if needUpdate:
        cmd = 'update appstores set version=%d where scheme is not null and version < 0;'%(maxVersion+1)
        mysqlCur.execute(cmd)
        mysqlConn.commit()
        _info("更新新版本")
        maxVersion += 1

    # 检查scheme目录是否存在
    targetFolder = os.path.join(".", "scheme")
    if not os.path.isdir(targetFolder):
        _info("创建scheme目录")
        os.makedirs(targetFolder)

    # 生成scheme json数据
    for i in range(1, maxVersion+1):
        for j in range(i+1, maxVersion+1):
            cmd = 'select * from appstores where version > %d and version <=%d and scheme is not null;'%(i, j)
            mysqlCur.execute(cmd)
            results = mysqlCur.fetchall()
            schemeList = {}
            for info in results:
                appInfo = AppInfo()
                appInfo.trackid = info[1]
                appInfo.name = info[2]
                appInfo.scheme = _encrypt(info[3])
                appInfo.icon60 = info[4]
                appInfo.icon512 = info[5]
                
                schemes = appInfo.scheme
                _info("schemes is %s"%info[3])
                _info("schemes encode is %s"%schemes)
                _info("schemes length is %d"%len(schemes))
                schemeList[appInfo.trackid] = appInfo.toDict()

            content = ""
            if indent:
                content = json.dumps(schemeList, indent=4)
            else:
                content = json.dumps(schemeList)
            targetPath = os.path.join(targetFolder, "extSchemeApps_%d_%d.json"%(j, i))
            open(targetPath, "w").write(content)

    # 生成最新所有的scheme json数据
    queryCmd = "select * from appstores where scheme != '';"
    mysqlCur.execute(queryCmd)
    results = mysqlCur.fetchall()
    schemeList = {}
    for info in results:
        appInfo = AppInfo()
        appInfo.trackid = info[1]
        appInfo.name = info[2]
        appInfo.scheme = _encrypt(info[3])
        appInfo.icon60 = info[4]
        appInfo.icon512 = info[5]

        schemes = appInfo.scheme
        _info("schemes is %s"%info[3])
        _info("schemes encode is %s"%schemes)
        _info("schemes length is %d"%len(schemes))
        schemeList[appInfo.trackid] = appInfo.toDict()

    content = ""
    if indent:
        content = json.dumps(schemeList, indent=4)
    else:
        content = json.dumps(schemeList)
    targetPath = os.path.join(targetFolder, "extSchemeApps.json")
    open(targetPath, "w").write(content)


import AppStoreConstants

host=AppStoreConstants.MYSQL_HOST
user=AppStoreConstants.MYSQL_PASSPORT
passwd=AppStoreConstants.MYSQL_PASSWORD
db=AppStoreConstants.MYSQL_DATABASE

def main(filepath=None, indent=False):
    mysqlConn = None
    mysqlCur  = None

    _info("=== Start Main ===")

    try:
        mysqlConn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, charset="utf8")
        mysqlCur  = mysqlConn.cursor()
        _info("Connect to %s@%s"%(host, user))
    except MySQLdb.Error,e:
        _info("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        return

    _generate(mysqlConn, mysqlCur, indent)

if __name__=="__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')

    workDir = os.path.dirname(os.path.realpath(sys.argv[0]))
    os.chdir(workDir) # 保证spider cache目录一致

    """
    python GenerateAppSchemes.py -f

    -f: format the json output
    """
    indent = False
    if "-f" in sys.argv:
        indent = True

    main(None, indent=indent)