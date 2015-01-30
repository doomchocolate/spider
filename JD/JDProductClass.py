#encoding=utf-8
from __future__ import unicode_literals

class JDProductInfo:

    def __init__(self, 
            product_id=-1, 
            product_title="", 
            product_intro="", 
            product_detail="",
            product_cover_img="",
            product_price="",
            product_price_tag="",
            buy_url=""):

        self.product_id = product_id
        self.product_title = product_title
        self.product_intro = product_intro
        self.product_detail = product_detail
        self.product_cover_img = product_cover_img
        self.product_price = product_price     # 当前出售价格
        self.product_price_tag = product_price_tag # 吊牌价
        self.buy_url = buy_url

        # 在获取商品详细信息的时候设置进去
        self.product_name = "" # 商品名
        self.product_brand = "" # 商品品牌
        self.product_publish_time = "" # 商品上架时间

        # 下面由于采集数据问题，暂时无用
        self.product_location = "" # 商品生产地
        self.product_compatibility = "" # 商品的兼容性
        self.product_function = "" # 商品的功能性
        self.product_taget_people = "" # 商品适用人群
        self.product_type = "" # 商品类型，腕戴式，头戴式

    def setProductId(self, product_id):
        self.product_id = product_id

    def setProductBuyUrl(self, buy_url):
        self.buy_url = buy_url

    def setProductName(self, product_name):
        self.product_name = product_name

    def setProductBrand(self, product_brand):
        self.product_brand = product_brand

    def setProductPublishTime(self, product_publish_time):
        self.product_publish_time = product_publish_time

    def setProductLocation(self, product_location):
        self.product_location = product_location

    def setProductCompatibility(self, product_compatibility):
        self.product_compatibility = product_compatibility

    def setProductFunction(self, product_function):
        self.product_function = product_function

    def setProductTargetPeople(self, product_taget_people):
        self.product_taget_people = product_taget_people

    def setProductType(self, product_type):
        self.product_type = product_type

    def __str__(self):
        result = []
        result.append("Product Info:")
        result.append("  product id: %s"%str(self.product_id))
        result.append("  product title: %s"%str(self.product_title))
        result.append("  product intro: %s"%str(self.product_intro))
        # result.append("  product detail: %.30s..."%str(self.product_detail))
        result.append("  product cover img: %s"%str(self.product_cover_img))
        result.append("  product price: %s"%str(self.product_price))
        result.append("  product price tag: %s"%str(self.product_price_tag))
        result.append("  product name: %s"%str(self.product_name))
        result.append("  product brand: %s"%str(self.product_brand))
        result.append("  product publis time: %s"%str(self.product_publish_time))
        # result.append("  product location: %s"%str(self.product_location))
        # result.append("  product compatibility: %s"%str(self.product_compatibility))
        # result.append("  product function: %s"%str(self.product_function))
        # result.append("  product taget people: %s"%str(self.product_taget_people))
        # result.append("  product type: %s"%str(self.product_type))
        return "\n".join(result) + "\n"

    # def __cmp__(self, other):
    #     if other is None:
    #         return 1

    #     try:
    #         _otherProductId = int(other.product_id)
    #         _productId = int(self.product_id)
    #         if _otherProductId == _productId:
    #             return 0
    #         elif _otherProductId < _productId:
    #             return 1
    #         else:
    #             return -1
    #     except Exception, e:
    #         return 1

    def toTuple(self):
        return (
            self.product_id, 
            self.product_title, 
            self.product_intro, 
            self.product_detail,
            self.product_cover_img,
            self.product_price,
            self.product_price_tag,
            self.buy_url,
            self.product_name,
            self.product_brand,
            self.product_publish_time)

    def getProductId(self):
        return self.product_id

    def getProductTitle(self):
        return self.product_title

    def getProductBuyUrl(self):
        return self.buy_url

    def setProductPrice(self, price):
        self.product_price = price

    def setProductPriceTag(self, price):
        self.product_price_tag = price

    def setProductDetail(self, detail):
        self.product_detail = detail

# product = JDProductInfo({})
# print product