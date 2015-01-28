DEBUG = False
if platform.system() == 'Windows':
    DEBUG = True

MYSQL_HOST     = "iam007.cskkndpfwwgp.ap-northeast-1.rds.amazonaws.com"
MYSQL_PASSPORT = "jiangerji"
MYSQL_PASSWORD = "eMBWzH5SIFJw5I4c"
MYSQL_DATABASE = "baidu"

if DEBUG:
    MYSQL_HOST="localhost"
    MYSQL_PASSPORT="root"
    MYSQL_PASSWORD="123456"
    MYSQL_DATABASE="baidu"
