# coding=UTF-8
# author: shuqing.zhou
import sys
from os.path import dirname, abspath
from datetime import datetime, date, timedelta
from pymongo import MongoClient

sys.path.append(dirname(dirname(abspath(__file__))))

from config.config_otc import *
from eggs.utils.utils import md5
from eggs.utils.log import logger


def clean_replica(days=1):
    logger.info('Start clean replica record from Mongo <{} {} {}>!'.format(DATA_HOST, DB_OTC, TABLE_OTC))
    client = MongoClient(DATA_HOST)
    coll = client[DB_OTC][TABLE_OTC]

    urls = set()
    fields = {"sid": 1}
    query = {"sid": {"$regex": "http"}, 'pub': {'$gte': str(date.today() - timedelta(days=days))}}
    for item in coll.find(query, fields):
        sid_md5 = md5(item["sid"])

        if sid_md5 in urls:
            coll.update({"_id": item["_id"]}, {'$set': {'stat': 0, 'upt': datetime.now()}})
        urls.add(sid_md5)
    client.close()
    logger.info('End clean replica record from Mongo <{} {} {}>!'.format(DATA_HOST, DB_OTC, TABLE_OTC))


if __name__ == '__main__':
    clean_replica()