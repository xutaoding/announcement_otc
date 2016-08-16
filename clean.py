# coding=UTF-8
# author: shuqing.zhou

from pymongo import MongoClient

from config.config_otc import *
from eggs.utils.utils import md5

coll = MongoClient(DATA_HOST)[DB_OTC][TABLE_OTC]

print coll.find({"sid": {"$regex": "http"}}).count()
urls = set()
for item in coll.find({"sid": {"$regex": "http"}}, {"src": 1}):
    if md5(item["src"]) in urls:
        print item["src"]
        coll.delete_one({"_id": item["_id"]})
    urls.add(md5(item["src"]))
