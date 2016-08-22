# coding=UTF-8
# author: shuqing.zhou
import sys
from os.path import dirname, abspath
from datetime import datetime, date, timedelta
from pymongo import MongoClient

sys.path.append(dirname(dirname(abspath(__file__))))

from config.config_otc import *
from eggs.utils.utils import md5


def clean_replica(days=0):
    client = MongoClient(DATA_HOST)
    coll = client[DB_OTC][TABLE_OTC]
    print('Clean replica data start!')

    urls = set()
    fields = {"sid": 1}
    query = {"sid": {"$regex": "http"}, 'pub': str(date.today() - timedelta(days=days))}
    for item in coll.find(query, fields):
        sid_md5 = md5(item["sid"])

        if sid_md5 in urls:
            coll.update({"_id": item["_id"]}, {'$set': {'stat': 0, 'upt': datetime.now()}})
        urls.add(sid_md5)
    client.close()
    print('Clean replica data end!')


if __name__ == '__main__':
    clean_replica()