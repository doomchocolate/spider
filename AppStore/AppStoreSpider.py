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

import CommonUtils
import Constants

from Base.BaseSpider import BaseSpider
import AppStoreConstants
from AppClass import AppInfo

"""
获取前100（500）的应用
http://www.appannie.com/apps/ios/top/china/overall/?device=iphone
"""
_APPSTORE_TABLE_NAME = "appstores"
class AppStoreSpider(BaseSpider):
    _CREATE_COMMAND = 'CREATE TABLE IF NOT EXISTS `%s` (\
          `id` INT NOT NULL AUTO_INCREMENT,\
          `trackid` TEXT NOT NULL,\
          `name` TEXT NOT NULL,\
          `scheme` TEXT NULL,\
          `icon60` TEXT NULL,\
          `icon512` TEXT NULL,\
          PRIMARY KEY (`id`));'%_APPSTORE_TABLE_NAME

    def __init__(self, host=Constants.MYSQL_HOST, user=Constants.MYSQL_PASSPORT, passwd=Constants.MYSQL_PASSWORD, db=Constants.MYSQL_DATABASE):
        BaseSpider.__init__(self, AppStoreSpider._CREATE_COMMAND, host, user, passwd, db)

        # if AppStoreConstants.DEBUG:
        #     print "clear table", _APPSTORE_TABLE_NAME
        #     self.clearTable(_APPSTORE_TABLE_NAME)

        self.htmlCacheDir = "cache" + os.path.sep + _APPSTORE_TABLE_NAME + os.path.sep + 'html'
        self.cacheFileName = "annie_%s.html"%time.strftime("%Y_%m_%H")

    def getUrlContent(self, url):
        target_path = os.path.join(".", self.htmlCacheDir)
        target_path = os.path.join(target_path, self.cacheFileName)

        if not os.path.isfile(target_path):
            load_web_page_js_dir = os.path.join(".", "bin")
            load_web_page_js = os.path.join(load_web_page_js_dir, "loadAnnie.js")
            command = 'phantomjs --load-images=false "%s" "%s" "%s"'%(load_web_page_js, url, target_path)

            state = os.system(command.encode("utf-8"))
            print "Load Annie page state:", state

        return open(target_path).read()

    def getApps(self, contents):
        doc = etree.HTML(contents)

        # 获取每一行，一行由3个内容组成， 免费榜, 付费榜，畅销榜组成
        rows = doc.xpath("//tbody[@id='storestats-top-table']/tr")
        rowCount = 1

        appsList = []
        appsTrackIds = set()

        for row in rows:
            items = row.xpath("./td")
            info = ""
            print rowCount
            for item in items:
                # 获取title
                titleDom = item.xpath(".//span[@class='oneline-info title-info']")

                # 获取track id
                trackid = item.xpath(".//span[@style='display:none']")
                # print trackid[0].text #dir(trackid[0])

                print "%13s %s"%(trackid[0].text, titleDom[0].get("title"))

                appInfo = self.getAppIcon(trackid[0].text)
                if appInfo is not None:
                    if appInfo.trackid not in appsTrackIds:
                        appsList.append(appInfo)
                        appsTrackIds.add(appInfo.trackid)
                        # print appInfo
                        self.insertToDB(appInfo)

            rowCount += 1

        # 打印需要插入的app
        # for i in appsList:
        #     print i

    def insertToDB(self, appInfo):
        _INSERT_COMMAND = 'insert into %s (trackid, name, icon60, icon512) values '%_APPSTORE_TABLE_NAME + "(%s,%s,%s,%s)"

        if not self.isInTable(_APPSTORE_TABLE_NAME, "trackid", appInfo.trackid):
            self.insert(_INSERT_COMMAND, appInfo.toTuple())
            print "insert to database:", appInfo.name
            # print appInfo

    def getAppIcon(self, trackid):
        # https://itunes.apple.com/lookup?id=414478124&country=cn
        url = "https://itunes.apple.com/lookup?id=%s&country=cn"%trackid
        appInfoJson = json.loads(self.requestUrlContent(url, self.htmlCacheDir, "app_%s.html"%trackid))
        results = appInfoJson.get("results")
        # print len(results), results
        appInfo = None
        if len(results) > 0:
            appInfo = AppInfo()
            appInfo.setAppInfo(results[0])

        return appInfo

    def start(self):
        spiderUrl = "http://www.appannie.com/apps/ios/top/china/overall/?device=iphone"
        contents = self.getUrlContent(spiderUrl)
        self.getApps(contents)

        self.finish()


def main():
    host=AppStoreConstants.MYSQL_HOST
    user=AppStoreConstants.MYSQL_PASSPORT
    passwd=AppStoreConstants.MYSQL_PASSWORD
    db=AppStoreConstants.MYSQL_DATABASE

    spider = AppStoreSpider(host, user, passwd, db)
    spider.start()

if __name__=="__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')

    workDir = os.path.dirname(os.path.realpath(sys.argv[0]))
    os.chdir(os.path.dirname(workDir)) # 保证spider cache目录一致

    logFile = CommonUtils.openLogFile(mode="w")

    oldStdout = sys.stdout  
    sys.stdout = logFile

    print "============================================"
    print "change work direcotory to workDir", workDir
    print "Start AppStore Spider:", time.asctime()

    main()

    logFile.close()  
    if oldStdout:  
        sys.stdout = oldStdout
