#encoding=utf-8
from __future__ import unicode_literals
import __init__ # 主要为了在没有加入到环境变量时，可以引用父目录的文件
import sys
import os
import time
import datetime
import re

import CommonUtils
from Base.BaseSpider import BaseSpider
from BaiduEvaluationClass import BaiduEvaluationInfo

_EVALUATION_TABLE_NAME = "evaluations"

class BaiduEvaluationSpider(BaseSpider):
    # 创建新闻表的命令
    _CREATE_COMMAND = 'CREATE TABLE IF NOT EXISTS `%s` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `evaluation_id` INT UNSIGNED NOT NULL, `product_id` INT UNSIGNED NOT NULL,  `create_time` DATETIME NULL,  `title` TEXT NULL,  `content` MEDIUMTEXT NULL,  `thumbnails` TEXT NULL,  `deploy_status` INT NULL DEFAULT 0,  PRIMARY KEY (`id`),  UNIQUE INDEX `id_UNIQUE` (`id` ASC))'%_EVALUATION_TABLE_NAME

    def __init__(self):
        BaseSpider.__init__(self, BaiduEvaluationSpider._CREATE_COMMAND)

        self.quota = 36

    def reMatch(self, content, pattern):
        pattern = re.compile(pattern)

        result = ""
        match = re.search(pattern, content)
        if match:
            result = match.group()
            result = unicode(result, "utf-8")

        return result

    def reFindall(self, content, pattern):
        pattern = re.compile(pattern)
        match = re.findall(pattern, content)

        return match

    # 获取title
    def getTitle(self, content):
        titlePattern = r'<title>[\s\S]*?</title>'
        title = self.reMatch(content, titlePattern)
        title = title[title.index(">")+1:title.rindex("</")]

        return title

    def getCreateTime(self, content):
        createTimePattern = r'duin.dateUtil.format[\s\S]*?;'
        createTime = self.reMatch(content, createTimePattern)

        try:
            startIndex = createTime.index("parseInt") + len("parseInt")
            startIndex = createTime.index("'", startIndex) + 1
            endIndex = createTime.index("'", startIndex)

            createTime = datetime.datetime.utcfromtimestamp(int(createTime[startIndex:endIndex]))
        except Exception, e:
            createTime = None
            print "无法获取创建时间。"      

        return createTime

    def getProductId(self, content):
        productIdPattern = r'product/view/[\s\S]*?.html'
        productId = self.reMatch(content, productIdPattern)
        try:
            productId = productId[productId.index("product/view/")+len("product/view/"):-5]
        except Exception, e:
            print "获取product id失败:", e

        return productId

    def getContent(self, content):
        evaluationContentPattern = r'<div class="d-artical-content" id="sourceContent">[\s\S]*?</div>'
        evaluationContent = self.reMatch(content, evaluationContentPattern)

        return evaluationContent

    def getThumbnails(self, content):
        imagePattern = r'<img[\s\S]*?>'
        _thumbnails = self.reFindall(content, imagePattern)

        thumbnails = []
        for thumbnail in _thumbnails:
            try:
                startIndex = thumbnail.index("src") + len("src")
                startIndex = thumbnail.index('"', startIndex) + 1
                endIndex = thumbnail.index('"', startIndex)
                thumbnail = thumbnail[startIndex:endIndex]
                thumbnails.append(thumbnail)
            except Exception, e:
                print "解析thumbnail失败:", e

        return thumbnails

    def getEvaluation(self, evaluationId):
        url = 'http://store.baidu.com/evaluation/view/%s.html'%str(evaluationId)
        cachePath = "cache" + os.path.sep + "evaluation" + os.path.sep + "html"
        htmlContent = self.requestUrlContent(url, cachePath, "%s.html"%evaluationId)

        if htmlContent == None:
            return None

        evaluationInfo = BaiduEvaluationInfo()
        evaluationInfo.setEvaluationId(evaluationId)

        # 获取title
        title = self.getTitle(htmlContent)
        # print "title:", title
        evaluationInfo.setTitle(title)

        # 获取创建时间
        createTime = self.getCreateTime(htmlContent)
        # print "create time:", createTime
        evaluationInfo.setCreateTime(createTime)

        if createTime == None:
            print "该测评可能不存在:", evaluationId
            try:
                # 删除缓存文件
                os.remove(os.path.join(cachePath, "%s.html"%evaluationId))
            except Exception, e:
                pass
            return None

        # 获取测评对应产品id
        productId = self.getProductId(htmlContent)
        # print "productId:", productId
        evaluationInfo.setProductId(productId)

        # 获取测评内容
        content = self.getContent(htmlContent)
        # print "content:", (content[0:min(20, len(content))]+"...")
        evaluationInfo.setContent(content)

        # 获取thumbnails
        thumbnails = self.getThumbnails(content)
        # print "thumbnail:", thumbnail
        evaluationInfo.setThumbnails(thumbnails)

        print evaluationInfo
        return evaluationInfo

    _INSERT_COMMAND = 'insert into %s (evaluation_id, product_id, create_time, title, content, thumbnails) values '%_EVALUATION_TABLE_NAME + "(%s,%s,%s,%s,%s,%s)"
    def start(self):
        evaluationId = 2

        # 从数据库中获取最大的evaluation id
        try:
            command = 'select max(evaluation_id) from %s'%_EVALUATION_TABLE_NAME
            self.mysqlCur.execute(command)
            evaluationId = self.mysqlCur.fetchone()[0] + 1
        except Exception, e:
            pass

        succCount = 0
        evaluationInfos = []
        failedEvaluationId = []
        failedCount = 0
        while True:
            evaluationInfo = self.getEvaluation(evaluationId)
            if evaluationInfo is None:
                failedEvaluationId.append(evaluationId)
                failedCount += 1

                if failedCount >= 10:
                    # 连续10次失败，退出
                    break
                evaluationId += 1
                continue

            failedCount = 0 # 重置连续失败次数

            evaluationInfos.append(evaluationInfo)
            succCount += 1

            if len(evaluationInfos) > 10000:
                break

            evaluationId += 1
            time.sleep(0.2)

        evaluationInfos.sort()
        insertFailedList = []
        for i in evaluationInfos:
            # 开始插入数据库
            print "插入数据库"
            print i, "\n"
            if self.insert(BaiduEvaluationSpider._INSERT_COMMAND, i.toTuple()):
                pass
            else:
                insertFailedList.append(i.getEvaluationId())
                print "插入数据库失败"
            
        print "不存在的evaluation id:", failedEvaluationId
        print "插入失败的evaluation id:", insertFailedList
        print "插入成功:", (len(evaluationInfos) - len(insertFailedList))
        self.finish()
        print "=========更新评测报告完成==========="
        
def main():
    spider = BaiduEvaluationSpider()
    spider.start()

    # evaluation = spider.getEvaluation(467)
    # spider.insert(BaiduEvaluationSpider._INSERT_COMMAND, evaluation.toTuple())
    # spider.finish()

if __name__ == "__main__":
    # if len(sys.argv) == 1:
    #     exit(1)

    reload(sys)
    sys.setdefaultencoding('utf-8')

    workDir = os.path.dirname(os.path.realpath(sys.argv[0]))
    os.chdir(workDir)

    logFile = CommonUtils.openLogFile()

    oldStdout = sys.stdout  
    sys.stdout = logFile

    print "============================================"
    print "change work direcotory to workDir", workDir
    print "Start BaiduEvaluationSpider:", time.asctime()

    main()

    logFile.close()  
    if oldStdout:  
        sys.stdout = oldStdout