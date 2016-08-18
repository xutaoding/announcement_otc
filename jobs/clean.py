# coding=UTF-8
# author: shuqing.zhou
from datetime import datetime
from pymongo import MongoClient

from config.config_otc import *
from eggs.utils.utils import md5


def clean_replica():
    client = MongoClient(DATA_HOST)
    coll = client[DB_OTC][TABLE_OTC]

    urls = set()
    fields = {"sid": 1}
    query = {"sid": {"$regex": "http"}}
    for item in coll.find(query, fields):
        sid_md5 = md5(item["sid"])

        if sid_md5 in urls:
            coll.update({"_id": item["_id"]}, {'$set': {'stat': 0, 'upt': datetime.now()}})
        urls.add(sid_md5)
    client.close()


if __name__ == '__main__':
    clean_replica()
