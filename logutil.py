#encoding=utf-8
import os
import time
import logging
import logging.handlers  

_fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(message)s'  
_formatter = logging.Formatter(_fmt)   # 实例化formatter  

_loggerMap = {}
def getLogger(loggerName, level=logging.DEBUG):
    _logPath = os.path.join(".", "log")
    if not os.path.isdir(_logPath):
        os.makedirs(_logPath)

    loggerName += time.strftime("_%Y_%m_%d")
        
    if _loggerMap.has_key(loggerName):
        return _loggerMap.get(loggerName)
    else:
        logFile = os.path.join(_logPath, 'iam007_%s_%s.log'%(loggerName, time.strftime("%Y_%m_%d")))
        print "logFile:", logFile
        # 实例化handler
        handler = logging.handlers.RotatingFileHandler(logFile)   
        # 为handler添加formatter
        handler.setFormatter(_formatter)      
        # 获取名为loggerName的logger
        logger = logging.getLogger(loggerName)
        # 为logger添加handler
        logger.addHandler(handler)
        logger.setLevel(level)

        _loggerMap[loggerName] = logger
        return logger

if __name__ == "__main__":
    logger = getLogger("this.is.test")
    logger.info("haha")
