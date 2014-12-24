#encoding=utf-8
from __future__ import unicode_literals
import __init__ # 主要为了在没有加入到环境变量时，可以引用父目录的文件
import sys
import os
import tempfile
import platform

import CommonUtils

PIC_SUFFIX = ["png", "jpg", "gif", "jpeg", "bmp"] # 图片文件后缀

class BaseInterface:

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

        state = 0
        if not os.path.isfile(target_path):
            # 在windows下是gb2312, 在ubuntu主机上应该是utf-8
            if platform.system() == 'Windows':
                state = os.system(command.encode("gb2312")) 
            else:
                state = os.system(command.encode("utf-8"))
        else:
            print url, "is already downloaded!"

        if ext[1:].lower() in PIC_SUFFIX:
            # print "requestUrlContent state", state
            if state != 0:
                return None

            return target_path

        return open(target_path).read()

    def aliasVerify(self, alias):
        _special_chars = "\\/%"
        # alias = alias.replace("-", "").strip()
        for i in _special_chars:
            alias = alias.replace(i, "-")

        if alias[0] == '-':
            alias = alias[1:]
        return alias

    def getValue(self, mysqlCursor, tableName, columnName, keyColumn, keyColumnValue, limit=-1):
        command = 'select %s from %s where `%s`="%s"'%(columnName, tableName, keyColumn, keyColumnValue)
        if limit > 0:
            command += " limit 0, %d"%limit

        result = []
        
        try:
            mysqlCursor.execute(command)
            result = mysqlCursor.fetchall()
        except Exception, e:
            pass

        return map(lambda x: x[0], result)
        
