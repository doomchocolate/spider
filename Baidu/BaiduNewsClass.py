#encoding=utf-8
from __future__ import unicode_literals

class BaiduNewsInfo:

    def __init__(self, infos):
        self.id = infos.get("id", 0)
        self.create_time = infos.get("create_time", "")
        self.title = infos.get("title", 0)
        self.excerpt = infos.get("excerpt", 0)
        self.status = infos.get("status", 0)
        self.comment_status = infos.get("comment_status", 0)
        self.thumbnails = infos.get("thumbnails", 0)
        self.source = infos.get("source", 0)
        self.cat_id = infos.get("cat_id", 0)
        self.comment_count = infos.get("comment_count", 0)
        self.like_count = infos.get("like_count", 0)
        self.weights = infos.get("weights", 0)
        self.content = ""

    def __cmp__(self, other):
        if other.create_time == self.create_time:
            return 0
        elif other.create_time < self.create_time:
            return 1
        else:
            return -1

    def __str__(self):
        result = []
        result.append("News Info:")
        result.append("  news id: %s"%str(self.id))
        result.append("  new title: %s"%str(self.title))
        result.append("  new excerpt: %s"%str(self.excerpt))
        result.append("  create_time: %s"%str(self.create_time))
        result.append("  status: %s"%str(self.status))
        result.append("  comment_status: %s"%str(self.comment_status))
        result.append("  thumbnails: %s"%str(self.thumbnails))
        result.append("  source: %s"%str(self.source))
        result.append("  cat_id: %s"%str(self.cat_id))
        result.append("  comment_count: %s"%str(self.comment_count))
        result.append("  like_count: %s"%str(self.like_count))
        result.append("  weights: %s"%str(self.weights))
        result.append("  content:%s"%(str(self.content[0:min(40, len(self.content))]))+"...")

        return "\n".join(result)

    def setContent(self, content):
        self.content = content

    def getId(self):
        return self.id

    def getTitle(self):
        return self.title

    def toTuple(self):
        return (
            self.id,
            self.create_time,
            self.title, 
            self.excerpt, 
            self.content,
            self.thumbnails,
            self.source)

# news1 = BaiduNewsInfo({})
# news1.create_time = "2014-12-12 18:05:16"

# news2 = BaiduNewsInfo({})
# news2.create_time = "2014-12-18 18:45:59"

# news3= BaiduNewsInfo({})
# news3.create_time = "2014-12-11 16:02:16"

# a = [news1, news2, news3]
# a.sort()

# for i in a:
#     print i


