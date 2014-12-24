#encoding=utf-8
from __future__ import unicode_literals
import __init__ # 主要为了在没有加入到环境变量时，可以引用父目录的文件
import sys
import os
import time
import platform
import random

import Image

from Base.BaseInterface import BaseInterface
import CommonUtils
import Tags

class AWSArticle(BaseInterface):

    def __init__(self, infoType, newsId, title, intro, detail, thumbnail, mysqlCursor=None, catId=8, buyUrl=None, createTime=None):
        """
        infoType: 新闻的类型，产品、测评或者普通新闻["news", "evaluation", "product"]
        newsId: 新闻的id
        title:  新闻的标题
        intro:  新闻的介绍
        thumbnail: 新闻的介绍图
        """
        self._infoType = infoType
        self._newsId = newsId
        self._title = title
        self._intro = intro
        self._detail = detail
        self._thumbnail = thumbnail
        self._catId = catId
        self._mysqlCursor = mysqlCursor
        self._buyUrl = buyUrl
        self._tags = None
        self._config = 0
        self._createTime = createTime

        # 网站的根目录
        WWW_ROOT = "/home/ubuntu/drupal/dreame-mall"
        if platform.system() == 'Windows':
            WWW_ROOT = ""

        self._TARGET_CACHE_DIR = "media"+os.path.sep+"tz_portfolio"+os.path.sep+"article"+os.path.sep+"cache"

        # 本地保存缩略图的路径
        self._thumbnailCachePath = os.path.join(WWW_ROOT, self._TARGET_CACHE_DIR)
        if not os.path.isdir(self._thumbnailCachePath):
            os.makedirs(self._thumbnailCachePath)

        # 发布者列表，随机在这个发布者列表中选择作者
        self._deployers = None
        if self._mysqlCursor is not None:
            self._mysqlCursor.execute('select id from erji_users')
            self._deployers = map(lambda x: x[0],  self._mysqlCursor.fetchall())

    def __str__(self):
        result = []
        result.append("Deploy Article Info:")
        result.append("  type is: %s"%str(self._infoType))
        result.append("  news id: %s"%str(self._newsId))
        result.append("  title: %s"%str(self._title))
        result.append("  intro: %s"%str(self._intro))
        result.append("  detail: %.40s..."%str(self._detail))
        result.append("  thumbnail: %s"%str(self._thumbnail))
        result.append("  cat id: %s"%str(self._catId))
        result.append("  product url: %s"%str(self._buyUrl))
        result.append("  tags are:")
        if self._tags is not None:
            result.append("    %s"%", ".join(map(lambda x: x[1], self._tags))) 

        return "\n".join(result)

    def downloadThumbnail(self):
        """
        下载缩略图
        """
        cacheDir = "cache" + os.path.sep + self._infoType + os.path.sep + "img" + os.path.sep + str(self._newsId)
        url = self._thumbnail
        thumbnailPath = self.requestUrlContent(url, cacheDir, CommonUtils.md5(url) + os.path.splitext(url)[-1])

        if not os.path.isfile(thumbnailPath):
            return None

        # 处理成5种尺寸, 按宽度自适应
        # XS:100, S:200, M:400, L:600, XL:900
        im = Image.open(thumbnailPath)
        width, height = im.size
        filename, ext = os.path.splitext(os.path.basename(thumbnailPath))

        thumbnailCachePath = self._thumbnailCachePath

        # XS
        _width = 100
        _heigh = _width * height / width
        target_file = os.path.join(thumbnailCachePath, filename+"_portfolio_"+"XS"+ext)
        out = im.resize((_width, _heigh), Image.ANTIALIAS)
        out.save(target_file)

        # S
        _width = 200
        _heigh = _width * height / width
        target_file = os.path.join(thumbnailCachePath, filename+"_portfolio_"+"S"+ext)
        out = im.resize((_width, _heigh), Image.ANTIALIAS)
        out.save(target_file)

        # M
        _width = 400
        _heigh = _width * height / width
        target_file = os.path.join(thumbnailCachePath, filename+"_portfolio_"+"M"+ext)
        out = im.resize((_width, _heigh), Image.ANTIALIAS)
        out.save(target_file)

        # L
        _width = 600
        _heigh = _width * height / width
        target_file = os.path.join(thumbnailCachePath, filename+"_portfolio_"+"L"+ext)
        out = im.resize((_width, _heigh), Image.ANTIALIAS)
        out.save(target_file)

        # XL
        _width = 900
        _heigh = _width * height / width
        target_file = os.path.join(thumbnailCachePath, filename+"_portfolio_"+"XL"+ext)
        out = im.resize((_width, _heigh), Image.ANTIALIAS)
        out.save(target_file)

        return os.path.join(self._TARGET_CACHE_DIR, filename+"_portfolio"+ext)

    ASSETS_RULES = '{"core.delete":{"6":1},"core.edit":{"6":1,"4":1},"core.edit.state":{"6":1,"5":1}}'
    def insertIntoAssets(self):
        cursor = self._mysqlCursor
        title = self._title

        # insert value into assets table, first step, return the id to insert content table
        cursor.execute('select lft, rgt, name from erji_assets where name like "com_content.article%" order by `id` desc limit 0, 1')
        _lft, _rgt, _name_id = cursor.fetchone()
        _lft += 2
        _lft = max(_lft, 151)
        _rgt += 2
        _rgt = max(_rgt, 152)
        name_id = int(_name_id.split(".")[-1]) + 1

        INSERT_ASSETS = 'insert into erji_assets (parent_id, lft, rgt, level, name, title, rules) values (%s,%s,%s,%s,%s,%s,%s)'
        assets_name = "com_content.article.%d"%(name_id)
        assets_values = [36, _lft, _rgt, 3, assets_name, title, AWSArticle.ASSETS_RULES]
        a = cursor.execute(INSERT_ASSETS, assets_values)
        
        return cursor.lastrowid

    #/**********************************************************/
    CONTENT_ATTRIBS = '{"show_title":"","link_titles":"","show_intro":"","show_category":"","link_category":"","show_parent_category":"","link_parent_category":"","show_author":"","link_author":"","show_create_date":"","show_modify_date":"","show_publish_date":"","show_item_navigation":"","show_icons":"","show_print_icon":"","show_email_icon":"","show_vote":"","show_hits":"","show_noauth":"","urls_position":"","alternative_readmore":"","article_layout":"","show_related_article":"","show_related_heading":"","related_heading":"","show_related_type":"","show_related_featured":"","related_image_size":"","related_orderby":"","show_publishing_options":"","show_article_options":"","show_urls_images_backend":"","show_urls_images_frontend":"","tz_portfolio_redirect":"","show_attachments":"","show_image":"","tz_use_image_hover":"","tz_image_timeout":"","portfolio_image_size":"","portfolio_image_featured_size":"","detail_article_image_size":"","show_image_gallery":"","detail_article_image_gallery_size":"","image_gallery_slideshow":"","show_arrows_image_gallery":"","show_controlNav_image_gallery":"","image_gallery_pausePlay":"","image_gallery_pauseOnAction":"","image_gallery_pauseOnHover":"","image_gallery_useCSS":"","image_gallery_slide_direction":"","image_gallery_animation":"","image_gallery_animSpeed":"","image_gallery_animation_duration":"","show_video":"","video_width":"","video_height":"","tz_show_gmap":"","tz_gmap_width":"","tz_gmap_height":"","tz_gmap_mousewheel_zoom":"","tz_gmap_zoomlevel":"","tz_gmap_latitude":"","tz_gmap_longitude":"","tz_gmap_address":"","tz_gmap_custom_tooltip":"","useCloudZoom":"","article_image_zoom_size":"","zoomWidth":"","zoomHeight":"","position":"","adjustX":"","adjustY":"","tint":"","tintOpacity":"","lensOpacity":"","softFocus":"","smoothMove":"","showTitle":"","titleOpacity":"","show_comment":"","tz_comment_type":"","tz_show_count_comment":"","disqusSubDomain":"","disqusApiSecretKey":"","disqusDevMode":"","show_twitter_button":"","show_facebook_button":"","show_google_button":"","show_extra_fields":"","field_show_type":""}'

    CONTENT_INSERT_COMMAND = 'insert into erji_content (asset_id, title, alias, introtext, `fulltext`, state, catid, created, created_by, created_by_alias, modified, modified_by, checked_out, checked_out_time, publish_up, publish_down, images, urls, attribs, version, ordering, metakey, metadesc, access, hits, metadata, featured, language, xreference) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

    def insertIntoContent(self, _asset_id):
        """
        _asset_id: 由insertIntoAssets返回的值
        _title: 文章的标题
        _introtext: 文章的简要介绍
        _fulltext: 文章全部内容
        """
        createOwner = random.choice(self._deployers)
        cursor = self._mysqlCursor

        asset_id = _asset_id
        title = self._title
        alias = self.aliasVerify(title)
        introtext = self._intro
        fulltext = self._detail
        state = 1
        catid = self._catId
        created = time.strftime("%Y-%m-%d %H:%M:%S")
        if self._createTime is not None:
            created = self._createTime
        created_by = createOwner
        created_by_alias = ""
        modified = time.strftime("%Y-%m-%d %H:%M:%S")
        if self._createTime is not None:
            modified = self._createTime
        modified_by = createOwner
        checked_out = createOwner
        checked_out_time = time.strftime("%Y-%m-%d %H:%M:%S")
        if self._createTime is not None:
            checked_out_time = self._createTime
        publish_up = "0000-00-00 00:00:00"
        publish_down = "0000-00-00 00:00:00"
        images = ""
        urls = ""
        attribs = AWSArticle.CONTENT_ATTRIBS
        version = 1
        ordering = 0
        metakey = '可穿戴,可穿戴设备,百度可穿戴设备,百度可穿戴,智能设备,智能可穿戴设备,超智能设备,百度智能设备,便携设备,便携智能设备,百度便携设备, 人体设备,智能人体设备,百度人体设备,便携人体设备,dulife,dulife平台,奇酷网,奇酷,360奇酷,小米酷玩,小米酷玩频道,百度硬件,智能硬件,硬件,智能移动设备,智能移动硬件,移动设备,移动硬件,可穿戴硬件,点名时间,母亲节'
        metadesc = ''
        access = 1
        hits = 1
        metadata = '{"robots":"","author":"","rights":"","xreference":""}'
        featured = 0
        language = "*"
        xreference = ""

        if self._buyUrl is not None and len(self._buyUrl) > 0:
            # 更新fulltext
            buyBtnCode = '<p class="jiangerji"><a class="btn btn-large btn-primary" href="%s" target="_blank">立即购买</a></p>\n'%self._buyUrl
            fulltext = buyBtnCode + fulltext
            # fulltext = fulltext.replace("'", "\\'")

        values = (asset_id, title, alias, introtext, fulltext, state, catid, created, created_by, created_by_alias, modified, modified_by, checked_out, checked_out_time, publish_up, publish_down, images, urls, attribs, version, ordering, metakey, metadesc, access, hits, metadata, featured, language, xreference)

        count = cursor.execute(AWSArticle.CONTENT_INSERT_COMMAND, values)

        if count > 0:
            return cursor.lastrowid
        else:
            return count

    # 插入到xref content table中
    XREF_INSERT_COMMAND = 'insert into erji_tz_portfolio_xref_content (contentid, groupid, images, images_hover, gallery, video, type, imagetitle, gallerytitle, videotitle, videothumb, attachfiles, attachtitle, attachold, audio, audiothumb, audiotitle, quote_author, quote_text, link_url, link_title, link_attribs) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    def insertXrefContent(self, _contentid, _images):
        contentid = _contentid
        groupid = 0
        images = _images
        images_hover = ""
        gallery = ""
        video = ""
        content_type = "image"
        imagetitle = ""
        gallerytitle = ""
        videotitle = ""
        videothumb = ""
        attachfiles = ""
        attachtitle = ""
        attachold = ""
        audio = ""
        audiothumb = ""
        audiotitle = ""
        quote_author = ""
        quote_text = ""
        link_url = ""
        link_title = ""
        link_attribs = '{"link_target":"_blank","link_follow":"nofollow"}'

        values = (contentid, groupid, images, images_hover, gallery, video, content_type, imagetitle, gallerytitle, videotitle, videothumb, attachfiles, attachtitle, attachold, audio, audiothumb, audiotitle, quote_author, quote_text, link_url, link_title, link_attribs)
        return self._mysqlCursor.execute(AWSArticle.XREF_INSERT_COMMAND, values)
    
    TAGS_INSERT_COMMAND = 'insert into erji_tz_portfolio_tags_xref (tagsid, contentid) values (%s,%s)'
    def insertTags(self, contentId):
        content = self._title + self._intro + self._detail
        self._tags = Tags.getTags(content)

        values = []
        for tag in self._tags:
            values.append((tag[0], contentId))

        try:
            self._mysqlCursor.executemany(AWSArticle.TAGS_INSERT_COMMAND, values)
        except Exception, e:
            print "插入Tags异常", e

    ARTICLE_DISABLE_TAGS = 0x00000001 # 对该文章不进行标签分类
    def addFlag(self, flag):
        self._config |= flag

    def deploy(self):
        """
        发布到网站中
        """
        if self._mysqlCursor is None:
            # mysql cursor is None
            return False

        # 下载thumbnail
        thumbnail = None
        if self._thumbnail is not None and len(self._thumbnail) > 0:
            thumbnail = self.downloadThumbnail()
            print "thumbnail:", thumbnail
            if thumbnail is None:
                print "下载thumbnail失败"
                return False

        # 插入assets表
        assetId = self.insertIntoAssets()
        if assetId < 0:
            print "插入assets表失败", assetId
            return False

        # 插入content表
        contentId = self.insertIntoContent(assetId)
        if contentId <= 0:
            print "插入content表失败", contentId
            return False

        # 插入应用图片
        if thumbnail is not None:
            state = self.insertXrefContent(contentId, thumbnail)
            if state <= 0:
                return False

        # 插入tags
        if (self._config & AWSArticle.ARTICLE_DISABLE_TAGS) != AWSArticle.ARTICLE_DISABLE_TAGS:
            self.insertTags(contentId)
        return True

def main():
    article = AWSArticle("test", 1, "title", "intro", "detail", 'http://bs.baidu.com/dulife/7e3348cc419c3aef06746ad87b77b625.jpg')
    article.deploy()

if __name__=="__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')

    workDir = os.path.dirname(os.path.realpath(sys.argv[0]))
    os.chdir(os.path.dirname(workDir))

    logFile = CommonUtils.openLogFile()

    oldStdout = sys.stdout  
    sys.stdout = logFile

    print "============================================"
    print "change work direcotory to workDir", workDir
    print "Start AWS Baidu Article Deploy:", time.asctime()

    main()

    logFile.close()  
    if oldStdout:  
        sys.stdout = oldStdout
