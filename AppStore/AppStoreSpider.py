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
          `addtime` TEXT NULL,\
          PRIMARY KEY (`id`));'%_APPSTORE_TABLE_NAME

    def __init__(self, host=Constants.MYSQL_HOST, user=Constants.MYSQL_PASSPORT, passwd=Constants.MYSQL_PASSWORD, db=Constants.MYSQL_DATABASE):
        BaseSpider.__init__(self, AppStoreSpider._CREATE_COMMAND, host, user, passwd, db)

        self.htmlCacheDir = "cache" + os.path.sep + _APPSTORE_TABLE_NAME + os.path.sep + 'html'
        self.cacheFileName = ""

        # if AppStoreConstants.DEBUG:
        #     print "clear table", _APPSTORE_TABLE_NAME
        #     self.clearTable(_APPSTORE_TABLE_NAME)

    def getUrlContent(self, url, cacheFile=None):
        target_path = os.path.join(".", self.htmlCacheDir)
        target_path = os.path.join(target_path, self.cacheFileName)

        if cacheFile is not None:
            target_path = cacheFile

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
        _INSERT_COMMAND = 'insert into %s (trackid, name, scheme, icon60, icon512, addtime) values '%_APPSTORE_TABLE_NAME + "(%s,%s,%s,%s,%s,%s)"

        if not self.isInTable(_APPSTORE_TABLE_NAME, "trackid", appInfo.trackid):
            self.insert(_INSERT_COMMAND, appInfo.toTuple())
            print "insert to database:", appInfo.name
        else:
            print "%s already in database!"%appInfo.name
            # print appInfo
        # exit()

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

    def getCategorys(self, contents):
        doc = etree.HTML(contents)

        # 获取每一行，一行由3个内容组成， 免费榜, 付费榜，畅销榜组成
        categorys = doc.xpath("//ul[@class='picker-col']/li")
        for category in categorys:
            print category
        

    def start(self):
        categorys = ["overall", "music"]

        for category in categorys:
            self.cacheFileName = "%s_%s.html"%(category, time.strftime("%Y_%m_%d_%H"))

            spiderUrl = "http://www.appannie.com/apps/ios/top/china/%s/?device=iphone"%category
            contents = self.getUrlContent(spiderUrl)
            
            # self.cacheFileName = "annie.html"
            
            self.getApps(contents)
            # self.getCategorys(contents)

        self.finish()

    def validateData(self):
        # 在schemeApps.json查找已经定义了的应用的scheme
        a = open("./AppStore/schemeApps.json", "r")
        allSchemes = json.load(a)
        # print len(allSchemes), type(allSchemes)

        schemeMap = {}

        for scheme in allSchemes.keys():
            # print scheme, type(allSchemes[scheme])
            for trackid in allSchemes.get(scheme):
                schemes = []
                if schemeMap.has_key(trackid):
                    schemes = schemeMap[trackid]
                schemes.append(scheme)
                schemeMap[trackid] = schemes
        print "Load scheme map finish!", len(schemeMap.keys())

        queryCmd = "select trackid, name from %s"%_APPSTORE_TABLE_NAME
        try:
            self.mysqlCur.execute(queryCmd)
            results = self.mysqlCur.fetchall()
            trackids = map(lambda x: int(x[0]), results)
            names = map(lambda x: x[1], results)
            count = 0
            for trackid in trackids:
                if schemeMap.has_key(trackid):
                    # 目前有scheme的应用
                    print trackid, schemeMap.get(trackid), names[count]
                    # update cmd
                    updateCmd ="UPDATE appstores SET `scheme`='%s' WHERE `trackid`='%s';"%(":".join(schemeMap.get(trackid)), trackid)
                    self.mysqlCur.execute(updateCmd)
                    print updateCmd
                count += 1
        except Exception, e:
            print e

        self.finish()

    def updateIcon60to175(self):
        urlFormat = "https://itunes.apple.com/cn/app/id%s?mt=8"

        queryCmd = "select trackid from %s;"%_APPSTORE_TABLE_NAME
        self.mysqlCur.execute(queryCmd)

        results = self.mysqlCur.fetchall()
        count = 0
        for i in results:
            trackid = i[0]
            url = urlFormat%i

            cacheFile = os.path.join(self.htmlCacheDir, "itunes_%s.html"%trackid)
            content = None
            try:
                content = self.getUrlContent(url, cacheFile)
            except Exception, e:
                continue

            doc = etree.HTML(content)

            rows = doc.xpath("//div[@class='lockup product application']//img[@class='artwork']")
            for row in rows:
                icon60 = row.get("src")
                icon512 = row.get("src-swap-high-dpi")

                updateCmd = "UPDATE appstores SET `icon60`='%s', icon512='%s' WHERE `trackid`='%s';"%(icon60, icon512, trackid)
                self.mysqlCur.execute(updateCmd)

            count += 1
            # if count > 50:#debug
            #     break

        self.finish()


    def paserAppList(self):
        # 将AppList.plist中的scheme提炼出来,并存入数据库中
        doc = etree.HTML(open("./AppStore/AppList.plist.xml", "r").read())

        # 获取每一行，一行由3个内容组成， 免费榜, 付费榜，畅销榜组成
        categorys = doc.xpath("//plist/dict/array/dict")

        count = 0
        for category in categorys:
            count += 1
            if count % 50 == 0:
                self.commit()

            children = category.getchildren()

            trackid = -1
            appName = ""
            appScheme = ""

            index = 0
            while index < len(children):
                child = children[index]

                # 获得track id
                if child.tag == "key":
                    if child.text == "id":
                        trackid = children[index+1].text

                # 获得app name
                if child.tag == "key":
                    if child.text == "nm":
                        appName = children[index+1].text

                index += 1

            # 获取shceme
            schemeInfo = category.xpath("./array/dict")[0]
            children = schemeInfo.getchildren()
            index = 0
            while index < len(children):
                child = children[index]

                # 获得track id
                if child.tag == "key":
                    if child.text == "url":
                        appScheme = children[index+1].text
                        break
                index += 1

            print trackid, appName, appScheme
            if int(trackid) < 100000:
                # 系统应用，暂时忽略
                pass
            else:
                appInfo = self.getAppIcon(trackid)
                if appInfo is not None:
                    # print "get app info:", appInfo
                    appInfo.scheme = appScheme.replace('://', '')
                    if not self.isInTable(_APPSTORE_TABLE_NAME, "trackid", trackid):
                        print "not in table!"
                        self.insertToDB(appInfo)
                        print "insert:"
                    else:
                        # 更新scheme
                        updateCmd ="UPDATE appstores SET `scheme`='%s' WHERE `trackid`='%s';"%(appInfo.scheme, trackid)
                        self.mysqlCur.execute(updateCmd)
                        print "update:"

                    print " ", appInfo
                else:
                    print " ", trackid, appName, " not exsits.\n"

        self.finish()

    def generateSchemeList(self):
        queryCmd = "select * from %s where scheme != '';"%_APPSTORE_TABLE_NAME
        self.mysqlCur.execute(queryCmd)
        results = self.mysqlCur.fetchall()
        schemeList = {}
        for info in results:
            appInfo = AppInfo()
            appInfo.trackid = info[1]
            appInfo.name = info[2]
            schemes = info[3].split(":")
            appInfo.icon60 = info[4]
            appInfo.icon512 = info[5]
            for scheme in schemes:
                if len(scheme.strip()) == 0:
                    continue
                schemeList[scheme] = appInfo.toDict()

        content = json.dumps(schemeList, indent=4)
        open("./AppStore/extSchemeApps.json.1", "w").write(content)

def main():
    host=AppStoreConstants.MYSQL_HOST
    user=AppStoreConstants.MYSQL_PASSPORT
    passwd=AppStoreConstants.MYSQL_PASSWORD
    db=AppStoreConstants.MYSQL_DATABASE

    spider = AppStoreSpider(host, user, passwd, db)
    # spider.start()
    spider.updateIcon60to175()

def validateData():
    host=AppStoreConstants.MYSQL_HOST
    user=AppStoreConstants.MYSQL_PASSPORT
    passwd=AppStoreConstants.MYSQL_PASSWORD
    db=AppStoreConstants.MYSQL_DATABASE

    spider = AppStoreSpider(host, user, passwd, db)
    spider.validateData()

def paserAppList():
    host=AppStoreConstants.MYSQL_HOST
    user=AppStoreConstants.MYSQL_PASSPORT
    passwd=AppStoreConstants.MYSQL_PASSWORD
    db=AppStoreConstants.MYSQL_DATABASE

    spider = AppStoreSpider(host, user, passwd, db)
    spider.paserAppList()

def generateSchemeList():
    host=AppStoreConstants.MYSQL_HOST
    user=AppStoreConstants.MYSQL_PASSPORT
    passwd=AppStoreConstants.MYSQL_PASSWORD
    db=AppStoreConstants.MYSQL_DATABASE

    spider = AppStoreSpider(host, user, passwd, db)
    spider.generateSchemeList()

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

    if "generate" in sys.argv:
        generateSchemeList()
    else:
        main()

    logFile.close()  
    if oldStdout:  
        sys.stdout = oldStdout
