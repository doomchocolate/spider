#encoding=utf-8
from __future__ import unicode_literals
import __init__ # 主要为了在没有加入到环境变量时，可以引用父目录的文件
import sys
import os
import time
import json
import re

import CommonUtils
from Base.BaseSpider import BaseSpider
from BaiduNewsClass import BaiduNewsInfo

class BaiduNewsSpider(BaseSpider):
    # 创建新闻表的命令
    _CREATE_COMMAND = 'CREATE TABLE IF NOT EXISTS `test`.`news` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `news_id` INT UNSIGNED NOT NULL,  `create_time` DATETIME NULL,  `title` VARCHAR(255) NULL,  `summary` MEDIUMTEXT NULL,  `content` MEDIUMTEXT NULL,  `thumbnails` TEXT NULL,  `source` TEXT NULL,  `deploy_status` INT NULL DEFAULT 0,  PRIMARY KEY (`id`),  UNIQUE INDEX `id_UNIQUE` (`id` ASC))'

    def __init__(self):
        BaseSpider.__init__(self, BaiduNewsSpider._CREATE_COMMAND)

        self.quota = 36

    # 解析新闻简要列表
    def parseNewsList(self, content):
        result = []

        all = json.loads(content)
        error_code = all.get("error_code")
        error_msg = all.get("error_msg")
        totalCount = -1
        if error_code == 0:
            # 获取成功
            data = all.get("data")
            news_list = data.get("list")
            totalCount = data.get("total")
            for news in news_list:
                news_info = BaiduNewsInfo(news)
                result.append(news_info)
        else:
            # 获取失败
            print "获取新闻列表失败，", error_msg

        return totalCount, result

    def getNewsContent(self, news):
        newsId = news.getId()
        url = "http://store.baidu.com/news/%s.html"%newsId
        content = self.requestUrlContent(url, "cache"+os.path.sep+"html", "%s.html"%newsId)

        # 获取summary
        summary_pattern = r'<div class=\"d-summary\">[\s\S]*?</div>'
        pattern = re.compile(summary_pattern)

        summary = ""
        match = re.search(pattern, content)
        if match:
            summary = match.group()
            summary = unicode(summary, "utf-8")
            summary = summary[summary.index(">")+1:summary.rindex("</div>")]

        # 获取content
        content_pattern = r'<div class="d-artical-content" id="sourceContent">[\s\S]*?</div>'
        pattern = re.compile(content_pattern)

        html_content = ""
        match = re.search(pattern, content)
        if match:
            html_content += match.group()

        news.setContent(html_content)

    # 插入table命令
    _INSERT_COMMAND = 'insert into news (create_time, title, summary, content, thumbnails, source) values (%s,%s,%s,%s,%s,%s)'
    def start(self):
        currentCount = self.getTableCount("news")

        index = 1
        urlFormat = "http://store.baidu.com/news/api/list?pn=%%d&limit=%d&_=%%s"%self.quota

        updateNewsList = []

        while True:
            url = urlFormat%(index, str(int(time.time()*100)))
            totalCount, newsList = self.parseNewsList(self.requestUrlContent(url))

            for news in newsList:
                # 检查是否已经在数据库中了

                # 不数据库中
                self.getNewsContent(news)
                time.sleep(0.1)
                if self.insert(BaiduNewsSpider._INSERT_COMMAND, news.toTuple()):
                    currentCount += 1
                else:
                    print "插入失败:", news.getId(), news.getTitle()
                print news
                print "****************"

            if len(newsList) < self.quota:
                break

            time.sleep(0.1)
            index += 1

            if index > 60:
                break

        # 完成抓取任务
        self.finish()

def main():
    spider = BaiduNewsSpider()
    spider.start()
    # spider.getTableCount("news")

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
    print "Start ArticleUtils:", time.asctime()

    main()

    logFile.close()  
    if oldStdout:  
        sys.stdout = oldStdout