#encoding=utf-8
from __future__ import unicode_literals

class BaiduProductInfo:

    def _init(self):
        self.product_id = -1
        self.product_name = ""
        self.product_title = ""
        self.product_intro = ""
        self.product_detail = ""
        self.product_cover_img = ""
        self.product_create_time = ""
        self.product_modified_time = ""
        self.product_price = ""
        self.evaluation_count = 0
        self.product_thumbnails = []
        self.buy_url = ""

    def __init__(self, infos):
        # infos is a dict
        self._init()
        if type(infos) != type({}):
            return

        self.product_id = infos.get("product_id", -1)
        self.product_name = infos.get("product_name", "")
        self.product_title = infos.get("product_title", "")
        self.product_intro = infos.get("product_intro", "")
        self.product_cover_img = infos.get("product_cover_img", "")
        self.product_create_time = infos.get("product_create_time", "")
        self.product_modified_time = infos.get("product_modified_time", "")
        self.product_price = infos.get("product_price", -1)
        self.evaluation_count = infos.get("evaluation_count", 0)
        self.product_thumbnails = infos.get("product_thumbnail", [])

    def __str__(self):
        result = []
        result.append("Product Info:")
        result.append("  product id: %s"%str(self.product_id))
        result.append("  product name: %s"%str(self.product_name))
        result.append("  product title: %s"%str(self.product_title))
        result.append("  product intro: %s"%str(self.product_intro))
        result.append("  product detail: %.30s..."%str(self.product_detail))
        result.append("  product cover img: %s"%str(self.product_cover_img))
        result.append("  product create time: %s"%str(self.product_create_time))
        result.append("  product modified time: %s"%str(self.product_modified_time))
        result.append("  product price: %s"%str(self.product_price))
        result.append("  evaluation count: %s"%str(self.evaluation_count))
        result.append("  product buy url: %s"%str(self.buy_url))
        result.append("  product thumbnails:")
        for i in self.product_thumbnails:
            result.append("    %s"%str(i))

        return "\n".join(result)

    def __cmp__(self, other):
        if other is None:
            return 1

        try:
            _otherProductId = int(other.product_id)
            _productId = int(self.product_id)
            if _otherProductId == _productId:
                return 0
            elif _otherProductId < _productId:
                return 1
            else:
                return -1
        except Exception, e:
            return 1

    def toTuple(self):
        return (
            self.product_id, 
            self.product_name, 
            self.product_title, 
            self.product_intro, 
            self.product_detail,
            self.product_cover_img,
            self.product_create_time,
            self.product_modified_time,
            self.product_price,
            self.evaluation_count,
            str(self.product_thumbnails),
            self.buy_url)

    def getId(self):
        return self.product_id

    def getName(self):
        return self.product_name

    def setDetail(self, detail):
        self.product_detail = detail

    def setProductThumbnails(self, product_thumbnails):
        self.product_thumbnails = product_thumbnails

    def setBuyUrl(self, buy_url):
        self.buy_url = buy_url

# product = BaiduProductInfo({})
# print product