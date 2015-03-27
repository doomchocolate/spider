import platform
DEBUG = False

if platform.system() == 'Windows':
    DEBUG = False

MYSQL_HOST     = "jiangerji.mysql.rds.aliyuncs.com"
MYSQL_PASSPORT = "jiangerji"
MYSQL_PASSWORD = "eMBWzH5SIFJw5I4c"
MYSQL_DATABASE = "spider"

if DEBUG:
    MYSQL_HOST="localhost"
    MYSQL_PASSPORT="root"
    MYSQL_PASSWORD="123456"
    MYSQL_DATABASE="spider"

URL_MAP = {
    "all": "http://www.appannie.com/apps/ios/top/china/overall/?device=iphone",
    "music": "http://www.appannie.com/apps/ios/top/china/music/?device=iphone"
}
