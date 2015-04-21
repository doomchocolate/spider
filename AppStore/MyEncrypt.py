#encoding=utf-8
from __future__ import unicode_literals
import __init__ # 主要为了在没有加入到环境变量时，可以引用父目录的文件
import os

from ctypes import *

class _my_string(Structure):
    _fields_ =[('length', c_int),  
               ('text', c_char_p)]

soPath = os.path.join(os.getcwd(), 'myencrypt.so')
libEnc = cdll.LoadLibrary(soPath)

def encrypt(input):
    if input is None or len(input) == 0:
        return ""
    inputLength = len(input)

    libEnc._encrypt.restype = POINTER(_my_string)   

    encResult = libEnc._encrypt(input, inputLength)

    # print "text", encResult.contents.text
    return encResult.contents.text
