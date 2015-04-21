#encoding=utf-8
from ctypes import *
import os
import sys
import platform
import time

# import MySQLdb

reload(sys)
sys.setdefaultencoding('utf-8')

if platform.system() != 'Windows' or True:
    soPath = os.path.join(os.getcwd(), 'myencrypt.so')
    libEnc = cdll.LoadLibrary(soPath)

def _info(message):
    # _logger = logutil.getLogger("CommitServer")
    # _logger.info(message)
    print message

def _debug(message):
    # _logger = logutil.getLogger("CommitServer")
    # _logger.debug(message)
    print message

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


class _my_string(Structure):
    _fields_ =[('length', c_int),  
               ('text', c_char_p)]  

def encrypt(input):
    # return input
    if input is None or len(input) == 0:
        return ""
    inputLength = len(input)

    libEnc._encrypt.restype = c_char_p  

    encResult = libEnc._encrypt(create_string_buffer(input), inputLength)

    # print "text", encResult.contents.text
    return encResult

def decrypt(input):
    if input is None or len(input) == 0:
        return ""
    inputLength = len(input)

    # libEnc._decrypt.restype = POINTER(_my_string)  
    libEnc._decrypt.restype = c_char_p 

    inputBuffer = input

    decResult = libEnc._decrypt(inputBuffer, inputLength)

    return decResult

import random
_alphate = "qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPLKJHGFDSAZXCVBNM0987654321"
_LEN = len(_alphate)
def genRandomString():
    length = random.randint(4, 30)
    a = []
    for i in range(length):
        a.append(_alphate[random.randint(0, _LEN-1)])
    return "".join(a)

def testEnc():
    a = "ed2k"
    print encrypt(a)
    exit()

    # print "aaa=["
    fp = open("enc.txt", "w")
    for i in xrange(10000):
        scheme = genRandomString()
        # print "scheme is", scheme
        # print "scheme length is", len(scheme)

        scheme = "e2dk"

        encResult = encrypt(scheme)
        fp.write("%s:%s\n"%(scheme, encResult))
        break
        # print '"%s",'%encResult 
        # print "encode result", encResult
        # decResult = decrypt(encResult)
        # # print "decode result", decResult
        # if decResult != scheme:
        #     print "scheme is", scheme
        #     print "scheme length is", len(scheme)
        #     print "decResult is", decResult
    # print "]"
    fp.close()
    # break
def testDec():
    fp = open("enc.txt", "r")
    out = open("dec.txt", "w")
    for line in fp.readlines():
        scheme, encResult = line.split(":")
        decResult = decrypt(encResult)
        # out.write(decResult+":"+scheme+"\n")
        # out.flush()
        if scheme != decResult:
            print "decResult", decResult
            print "scheme", scheme
            out.write(decResult+":"+scheme+"\n")
            out.flush()
    out.close()

def test():
    testEnc()
    print "Finish enc"
    # testDec()

def main():
    initMysql()

    cmd = 'select scheme from appstores where scheme is not null;'
    _mysqlCur.execute(cmd)

    schemes = _mysqlCur.fetchall()
    count = 0
    for j in range(100):
        for i in schemes:
            scheme = i[0]
            print "", count
            count += 1
            print "encrypt", scheme
            encResult = encrypt(scheme)
            print "encode result", encResult
            # decResult = decrypt(encResult)
            # print "decode result", decResult
            # break

    deinitMysql()

if __name__ == "__main__":
    test()
