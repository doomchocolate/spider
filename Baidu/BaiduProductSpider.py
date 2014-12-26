#encoding=utf-8
from __future__ import unicode_literals
import __init__ # 主要为了在没有加入到环境变量时，可以引用父目录的文件
import sys
import os
import platform
import time
import json
import re

import CommonUtils
import Constants

from Base.BaseSpider import BaseSpider
from BaiduProductClass import BaiduProductInfo

_PRODUCT_TABLE_NAME = "products"
_QUOTA = 36

class BaiduProductSpider(BaseSpider):
    # 创建新闻表的命令
    _CREATE_COMMAND = 'CREATE TABLE IF NOT EXISTS `%s` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `product_id` INT UNSIGNED NOT NULL, `product_name` TEXT NULL,  `product_title` TEXT NULL, `product_intro` TEXT NULL, `product_detail` TEXT NULL, `product_cover_img` TEXT NULL,  `product_create_time` DATETIME NULL,  `product_modify_time` DATETIME NULL, `product_price` FLOAT NULL DEFAULT 0, `evaluation_count` INT NULL DEFAULT 0, `product_thumbnails` TEXT NULL,  `buy_url` TEXT NULL,  `deploy_status` INT NULL DEFAULT 0,  PRIMARY KEY (`id`),  UNIQUE INDEX `id_UNIQUE` (`id` ASC))'%_PRODUCT_TABLE_NAME

    def __init__(self, host=Constants.MYSQL_HOST, user=Constants.MYSQL_PASSPORT, passwd=Constants.MYSQL_PASSWORD, db=Constants.MYSQL_DATABASE):
        BaseSpider.__init__(self, BaiduProductSpider._CREATE_COMMAND, host, user, passwd, db)

        self.htmlCacheDir = "cache" + os.path.sep + _PRODUCT_TABLE_NAME + os.path.sep + 'html'

    def parserProductsList(self, content):
        result = []
        total_count = -1

        all = json.loads(content)
        error_code = all.get("error_code")
        error_msg = all.get("error_msg")
        if error_code == 0:
            # 获取成功
            data = all.get("data")

            total_count = data.get("total")
            product_list = data.get("list")
            for product in product_list:
                product_info = BaiduProductInfo(product)
                result.append(product_info)
        else:
            # 获取失败
            print "获取产品列表失败，", error_msg

        return total_count, result

    def getProductDetail(self, product):
        url = "http://store.baidu.com/product/view/%s.html"%str(product.getId())
        content = self.requestUrlContent(url, self.htmlCacheDir, "%s.html"%str(product.getId()))

        # 获取product detail
        pattern = r'<div class=\"product-intro\">[\s\S]*?</div>'
        intro = self.reMatch(content, pattern)
        try:
            intro = intro[intro.index(">")+1:intro.rindex("</div>")]
            product.setIntro(intro)
        except Exception, e:
            print "获取Product Intro异常:", e

        # 获取product detail
        pattern = r'<div class=\"product-detail\">[\s\S]*?</div>'
        detail = self.reMatch(content, pattern)
        # try:
        #     detail = detail[detail.index(">")+1:detail.rindex("</div>")]
        # except Exception, e:
        #     print "获取Product Detail异常:", e

        product.setDetail(detail)

        # 获取product thumbnails
        pattern = r'<div class=\"wrap clearfix\">[\s\S]*?</div>'
        thumbnailsContent = self.reMatch(content, pattern)

        imagePattern = r'<img[\s\S]*?>'
        _thumbnails = self.reFindall(thumbnailsContent, imagePattern)

        productThumbnails = []
        for thumbnail in _thumbnails:
            try:
                startIndex = thumbnail.index("src") + len("src")
                startIndex = thumbnail.index('"', startIndex) + 1
                endIndex = thumbnail.index('"', startIndex)
                thumbnail = thumbnail[startIndex:endIndex]
                productThumbnails.append(thumbnail)
            except Exception, e:
                print "解析thumbnail失败:", e
        product.setProductThumbnails(productThumbnails)

        # buy url
        try:
            buyUrlPattern = r'<div class=\"buy\">[\s\S]*?</div>'
            buyUrl = self.reMatch(content, buyUrlPattern)
            http_pattern = r'http[\s\S]*?\"'
            buyUrl = self.reMatch(buyUrl, http_pattern)
            buyUrl = buyUrl.strip()
            buyUrl = buyUrl[0:buyUrl.rindex('"')].strip()
            product.setBuyUrl(buyUrl)
        except Exception, e:
            pass

    def start(self):
        # 获取已经抓取的产品数量
        currentCount = self.getTableCount(_PRODUCT_TABLE_NAME)
        print "目前已有产品数量:", currentCount

        index = 1
        # http://store.baidu.com/product/api/recommendList?cat_id=0&orderBy=time&order=desc&pn=%%d&limit=%d
        urlFormat = "http://store.baidu.com/product/api/recommendList?cat_id=0&orderBy=time&order=desc&pn=%%d&limit=%d"%_QUOTA

        updateProductsList = [] # 保存所有需要更新的产品数据

        while True:
            url = urlFormat%index
            totalCount, productList = self.parserProductsList(self.requestUrlContent(url))

            if currentCount >= totalCount:
                # 已经获取全部更新
                break

            # print totalCount
            for product in productList:
                # 检查是否已经抓取
                if self.isInTable(_PRODUCT_TABLE_NAME, "product_id", product.getId()):
                    # 已经在数据库中了
                    print "已经在数据中", product.getId(), product.getName(), "\n"
                    continue

                # 不数据库中，插入需要更新数据中
                self.getProductDetail(product)
                updateProductsList.append(product)

                currentCount += 1
                if currentCount >= totalCount:
                    # 已经获取全部更新
                    break

                time.sleep(0.1)

            if currentCount >= totalCount:
                # 已经获取全部更新
                break

            if len(productList) < _QUOTA:
                break

            time.sleep(0.1)
            index += 1

            if index > 1000:
                # 防止超时，死循环
                break

            # break # DEBUG

        # 对更新的数据进行排序，按照时间递增排序，然后再插入数据
        updateProductsList.sort()
        print "========开始插入数据库========"
        succCount = 0
        for product in updateProductsList:
            if self.insert(BaiduProductSpider._INSERT_COMMAND, product.toTuple()):
                succCount += 1
            else:
                print "插入失败:", product.getId(), product.getName()
            print product
            print "****************"

        # 完成抓取任务
        self.finish()
        print "更新", succCount, "条数据！"
        print "========完成更新数据库========"

    # 插入table命令
    _INSERT_COMMAND = 'insert into %s (product_id, product_name, product_title, product_intro, product_detail, product_cover_img, product_create_time, product_modify_time, product_price, evaluation_count, product_thumbnails, buy_url) values '%_PRODUCT_TABLE_NAME + "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

def main():
    host=Constants.MYSQL_HOST
    user=Constants.MYSQL_PASSPORT
    passwd=Constants.MYSQL_PASSWORD
    db=Constants.MYSQL_DATABASE

    if platform.system() == 'Windows':
        host="localhost"
        user="root"
        passwd="123456"
        db="test"

    spider = BaiduProductSpider(host, user, passwd, db)
    spider.start()
    # product = BaiduProductInfo({})
    # product.product_id = 2430
    # spider.getProductDetail(product)

if __name__=="__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')

    workDir = os.path.dirname(os.path.realpath(sys.argv[0]))
    os.chdir(os.path.dirname(workDir)) # 保证spider cache目录一致

    logFile = CommonUtils.openLogFile()

    oldStdout = sys.stdout  
    sys.stdout = logFile

    print "============================================"
    print "change work direcotory to workDir", workDir
    print "Start Baidu Product Spider:", time.asctime()

    main()

    logFile.close()  
    if oldStdout:  
        sys.stdout = oldStdout
