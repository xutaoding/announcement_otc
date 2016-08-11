# -*- coding: utf-8 -*-
from os.path import join, abspath, dirname

refer_uri = 'http://www.neeq.com.cn/announcement'
URI = 'http://www.neeq.com.cn/disclosureInfoController/infoResult.do?callback='
FORM_DATA = {
      'disclosureType': '5',
      'page': '0',          # Change
      'companyCd': '',
      'isNewThree': '1',    # 新三板还是老三板
      'startTime': '',      # Change
      'endTime': '',        # Change
      'keyword': '关键字',
      'xxfcbj': ''
}

CRT_INDEX = "http://192.168.250.205:17081/indexer/services/indexes/delta.json?indexer=announce_otc&taskids="

PORT = 27017
DB_OTC = 'news'
# DATA_HOST = '192.168.100.20'      # 测试环境mongo
# DATA_HOST = '192.168.251.95'        # 上海环境mong95 <122.144.134.95>
DATA_HOST = '122.144.134.95'        # 上海环境mong95 外网
TABLE_OTC = 'announcement_otc'

DB_RULE = 'ada'
# RULE_HOST = '192.168.250.20'       # 测试环境mongo
RULE_HOST = '192.168.251.95'         # 上海环境mong95 <122.144.134.95>
# RULE_HOST = '122.144.134.95'        # 上海环境mong95 外网
TABLE_RULE = 'dict_announce_rule'

STOCK_DB = 'ada'
# STOCK_HOST = '192.168.250.20'          # 测试环境mongo
STOCK_HOST = '192.168.251.95'            # 上海环境mong95 <122.144.134.95>
# STOCK_HOST = '122.144.134.95'        # 上海环境mong95 外网
STOCK_TABLE = 'base_stock'

ROOT_PATH = join(dirname(dirname(abspath(__file__))), 'files').replace('\\', '/') + '/'

AWS_HOST = 's3.cn-north-1.amazonaws.com.cn'
BUCKET_NAME = 'cn.com.chinascope.dfs'
AWS_ACCESS_KEY_ID = 'AKIAPY6JJ76F67VDOGBA'
AWS_SECRET_ACCESS_KEY = 'VDW2yIQR453LL3tQ0VYNZBvH2NLBa9w2/YKsdJOP'

ROOT_AWS_KEY = 'announce/otc/'



