#encoding=utf-8
from __future__ import unicode_literals

class BaiduEvaluationInfo:
    def _init(self):
        self.evaluationid = -1  # 测评报告id
        self.productid = -1     # 测评产品id
        self.userid = -1        # 测评人员id
        self.title = ""         # 测评报告的title
        self.score = 0          # 测评报告的评分
        self.content = ""       # 测评报告的全部内容
        self.thumbnails = ""     # 测评报告的缩略图
        self.excerpt = ""       # 测评报告的简要介绍
        self.createTime = ""    # 测评报告创建时间

    def __init__(self, infos={}):
        # infos is a dict
        if type(infos) != type({}):
            self._init()
            return

        self.evaluationid = infos.get("id", -1)
        self.productid = infos.get("product_id", -1)
        self.userid = infos.get("user_id", -1)
        self.title = infos.get("title", "")
        self.score = infos.get("score", -1)
        self.content = infos.get("content", "")
        self.thumbnails = infos.get("thumbnail", "")
        self.excerpt = infos.get("excerpt", "")
        self.createTime = ""

    def __cmp__(self, other):
        if self.createTime == other.createTime:
            return 0
        elif self.createTime > other.createTime:
            return 1
        else:
            return -1

    def __str__(self):
        result = []
        result.append("Baidu Evalution Info:")
        result.append("  evaluation id: %s"%str(self.evaluationid))
        result.append("  product id: %s"%str(self.productid))
        result.append("  title: %s"%str(self.title))
        result.append("  content: %s"%str(self.content[0:min(40, len(self.content))]+"..."))
        result.append("  thumbnail: %s"%str(self.thumbnails))
        result.append("  create time: %s"%str(self.createTime))

        return "\n".join(result)

    def getEvaluationId(self):
        return self.evaluationid

    def setEvaluationId(self, evaluationid):
        self.evaluationid = evaluationid

    def setCreateTime(self, createTime):
        self.createTime = createTime

    def setProductId(self, productid):
        self.productid = productid

    def setTitle(self, title):
        self.title = title

    def setContent(self, content):
        self.content = content

    def setThumbnails(self, thumbnails):
        self.thumbnails = thumbnails

    def toTuple(self):
        return (
            self.evaluationid,
            self.productid,
            self.createTime,
            self.title, 
            self.content, 
            str(self.thumbnails))


if __name__ == "__main__":
    evaluation = BaiduEvaluationInfo({})
    print evaluation