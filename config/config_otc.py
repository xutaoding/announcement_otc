from os.path import join, abspath, dirname

refer_uri = 'http://www.neeq.com.cn/announcement'
URI = 'http://www.neeq.com.cn/controller/GetDisclosureannouncementPage?' \
      'type={0}&company_cd=&key=&subType=0&startDate={1}&endDate={2}&queryParams=0&page={3}'

CRT_INDEX = "http://192.168.250.205:17081/indexer/services/indexes/delta.json?indexer=announce_otc&taskids="

PORT = 27017
DB_OTC = 'news'
# DATA_HOST = '192.168.250.208'
DATA_HOST = '192.168.0.223'
TABLE_OTC = 'announcement_otc'

DB_RULE = 'ada'
RULE_HOST = '192.168.250.200'
TABLE_RULE = 'dict_announce_rule'

STOCK_DB = 'ada'
STOCK_HOST = '192.168.250.200'
STOCK_TABLE = 'base_stock'

ROOT_PATH = join(dirname(dirname(abspath(__file__))), 'files').replace('\\', '/') + '/'

AWS_HOST = 's3.cn-north-1.amazonaws.com.cn'
BUCKET_NAME = 'cn.com.chinascope.dfs'
AWS_ACCESS_KEY_ID = 'AKIAPY6JJ76F67VDOGBA'
AWS_SECRET_ACCESS_KEY = 'VDW2yIQR453LL3tQ0VYNZBvH2NLBa9w2/YKsdJOP'

ROOT_AWS_KEY = 'announce/otc/'

ANNOC_TYPE_ONE_DATE = ['2015-09-30']

ANNOC_TYPE_TWO_DATE = ['2015-09-30']

