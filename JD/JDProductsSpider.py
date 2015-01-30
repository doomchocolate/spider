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
from JDProductClass import JDProductInfo
import JDConstants

_PRODUCT_TABLE_NAME = "jd_products"

"""
京东获取价格地址：不要callback后的地址也可以
http://p.3.cn/prices/mgets?type=1&skuIds=J_1180220,J_1190842,J_1277115,J_1080134,J_1216677,J_1249086,J_1324046,J_1408129955,J_1300171,J_1043529,J_1062108,J_1438841729,J_1263386,J_974158,J_1439611719,J_1304381,J_1237923,J_1080316,J_1123441,J_1174528,J_1186906,J_1304388,J_1231673,J_1263132,J_1378504199,J_1231726,J_1231677,J_1304971,J_1174460,J_1264399,J_1189393,J_1277759,J_1085277,J_1292687,J_1242433,J_1147805,J_1309732887,J_1143642,J_1131554,J_1277752,J_1177415,J_1162655,J_1410992775,J_1129073,J_1159948,J_1277754,J_1253275,J_1035705,J_1144158,J_1264398,J_1241606,J_1285189,J_1448666423,J_1159947,J_1264401,J_1128143,J_1152084,J_1241603,J_1237937,J_1139992&area=1_72_2839&callback=jQuery8654670&_=1422331200130
"""

class JDProductSpider(BaseSpider):
    # 创建新闻表的命令
    _CREATE_COMMAND = 'CREATE TABLE IF NOT EXISTS `%s` (\
                  `id` INT NOT NULL AUTO_INCREMENT,\
                  `product_id` TEXT NOT NULL,\
                  `product_title` TEXT NOT NULL,\
                  `product_intro` TEXT NULL,\
                  `product_detail` TEXT NOT NULL,\
                  `product_cover_img` TEXT NULL,\
                  `product_price` DOUBLE NULL,\
                  `product_price_tag` DOUBLE NULL,\
                  `buy_url` TEXT NOT NULL,\
                  `product_name` TEXT NULL,\
                  `product_brand` TEXT NULL,\
                  `product_publish_time` DATETIME NULL,\
                  `state` INT NULL DEFAULT 1,\
                   PRIMARY KEY (`id`));'%_PRODUCT_TABLE_NAME

    def __init__(self, host=Constants.MYSQL_HOST, user=Constants.MYSQL_PASSPORT, passwd=Constants.MYSQL_PASSWORD, db=Constants.MYSQL_DATABASE):
        BaseSpider.__init__(self, JDProductSpider._CREATE_COMMAND, host, user, passwd, db)

        if JDConstants.DEBUG:
            print "clear table", _PRODUCT_TABLE_NAME
            self.clearTable(_PRODUCT_TABLE_NAME)

        self.htmlCacheDir = "cache" + os.path.sep + _PRODUCT_TABLE_NAME + os.path.sep + 'html'

    def parserProductsList(self, content):
        doc = etree.HTML(content)   
        nodes = doc.xpath("//li[@class='gl-item']") 
        # node.keys() element节点的所有的属性key
        # node.values() 所有key对应的values

        products = []
        for node in nodes:
            # 商品sku id
            product_id = node.get('data-sku')

            # 商品的购买地址
            buy_urls = node.xpath(".//div[@class='p-img']//a")
            buy_url = ""
            if len(buy_urls) > 0:
                buy_url = buy_urls[0].get("href")

            # 商品图片
            imgs = node.xpath(".//div[@class='p-img']//img")
            product_cover_img = ""
            if len(imgs) > 0:
                product_cover_img = imgs[0].get('data-lazy-img')

            # 商品价格, wget的方法无法获得价格

            # 商品名称
            names = node.xpath(".//div[@class='p-name p-name-type2']//a")
            product_title = ""
            if len(names) > 0:
                product_title = names[0].get("title")

            product = JDProductInfo(
                product_id=product_id,
                product_title=product_title,
                product_cover_img=product_cover_img,
                buy_url=buy_url)

            products.append(product)

        self.getProductPrices(products)

        return products

    # 获取并设置商品的价格和吊牌价格
    def getProductPrices(self, products):
        url_format = "http://p.3.cn/prices/mgets?type=1&skuIds=%s&area=1_72_2839"

        t = map(lambda x: x.getProductId(), products)
        t = map(lambda x: "J_"+x, t)
        price_tail = ",".join(t)
        url = url_format%price_tail

        prices_content = self.requestUrlContent(url, self.htmlCacheDir, "prices_%d.json"%self.page_index)
        prices_content = json.loads(prices_content)

        prices_map = {}
        for price_info in prices_content:
            product_id = price_info.get("id")[2:]
            product_price = price_info.get("p")
            product_price_tag = price_info.get("m")
            prices_map[product_id] = (product_price, product_price_tag)

        for product in products:
            try:
                (product_price, product_price_tag) = prices_map.get(product.getProductId())
                product.setProductPrice(product_price)
                product.setProductPriceTag(product_price_tag)
            except Exception, e:
                pass

    def getProductDetail(self, product):
        product_id = product.getProductId()
        buy_url = product.getProductBuyUrl()

        detail_content = self.requestUrlContent(buy_url, self.htmlCacheDir, "detail_%s.html"%str(product_id), js_enable=True)
        doc = etree.HTML(detail_content)
        detail_1 = doc.xpath("//div[@id='product-detail-1']//li")
        try:
            product_name            = detail_1[0].get("title")
            product.setProductName(product_name)

            product_id              = detail_1[1].get("title")
            product_brand           = detail_1[2].get("title")
            product.setProductBrand(product_brand)

            product_publish_time    = detail_1[3].get("title")
            product.setProductPublishTime(product_publish_time)

            product_weight          = detail_1[4].get("title")
            # 按照这种顺序，在不同的商品上会出现不同的属性，暂时去前5个属性
            # product_location        = detail_1[5].get("title")
            # product.setProductLocation(product_location)

            # product_compatibility   = detail_1[6].get("title")
            # product.setProductCompatibility(product_compatibility)

            # product_function        = detail_1[7].get("title")
            # product.setProductFunction(product_function)

            # product_taget_people    = detail_1[8].get("title")
            # product.setProductTargetPeople(product_taget_people)

            # product_type            = detail_1[9].get("title")
            # product.setProductType(product_type)
        except Exception, e:
            print "getProductDetail exception:", e

        
        details = doc.xpath("//div[@id='product-detail-1']//div[@class='detail-content-item']")
        if len(details) > 0:
            detail_item = details[0]
            imgs = detail_item.xpath(".//img[@data-lazyload]")
            for img in imgs:
                img_url = img.get("data-lazyload")
                img.set("data-lazyload", "done")
                img.set("src", img_url)
                # print etree.tostring(img)

            detail = etree.tostring(details[0], encoding="utf-8", pretty_print=True).replace("    ", "")
            product.setProductDetail(detail)

        # node.keys() element节点的所有的属性key
        # node.values() 所有key对应的values
        # print product
         
    def start(self):
        # 获取已经抓取的产品数量
        currentCount = 0

        url_format = "http://list.jd.com/list.html?cat=652,12345,12353&area=1,72,2839&page=%d"

        updateProductsList = [] # 保存所有需要更新的产品数据

        succCount = 0
        self.page_index = 1

        while True:
            print "==== 开始处理 ", self.page_index," ===="
            url = url_format%self.page_index
            products = self.parserProductsList(self.requestUrlContent(url, self.htmlCacheDir, "product_%d.html"%self.page_index))
            self.page_index += 1

            # 开始插入数据库
            for product in products:
                # 检查是否已经抓取
                if self.isInTable(_PRODUCT_TABLE_NAME, "product_id", product.getProductId()):
                    # 已经在数据库中了
                    print "已经在数据中", product.getProductId(), product.getProductTitle(), "\n"
                    continue

                # 不数据库中，插入需要更新数据中
                # 获取商品详情
                self.getProductDetail(product)
                print product
                if self.insert(JDProductSpider._INSERT_COMMAND, product.toTuple()):
                    succCount += 1
                else:
                    print "插入失败:", product.getProductId(), product.getProductTitle()

                if succCount%15 == 0:
                    self.commit()
                    # break
            # break
            # 目前暂时一次获取最多60个，所以低于60，就表示抓取完毕
            if len(products) < 60:
                break

            time.sleep(1)

        # 完成抓取任务
        self.finish()
        print "更新", succCount, "条数据！"
        print "========完成更新数据库========"

    # 插入table命令
    _INSERT_COMMAND = 'insert into %s (product_id, product_title, product_intro, product_detail, product_cover_img, product_price, product_price_tag, buy_url, product_name, product_brand, product_publish_time) values '%_PRODUCT_TABLE_NAME + "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

def main():
    host=JDConstants.MYSQL_HOST
    user=JDConstants.MYSQL_PASSPORT
    passwd=JDConstants.MYSQL_PASSWORD
    db=JDConstants.MYSQL_DATABASE

    spider = JDProductSpider(host, user, passwd, db)
    spider.start()
    # product = JDProductInfo()
    # product.setProductId("1453838631")
    # product.setProductBuyUrl("http://item.jd.com/1453838631.html")
    # spider.getProductDetail(product)

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
    print "Start Baidu Product Spider:", time.asctime()

    main()

    logFile.close()  
    if oldStdout:  
        sys.stdout = oldStdout
