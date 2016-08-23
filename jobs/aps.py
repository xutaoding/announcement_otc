# -*- coding: utf-8 -*-
import re
import sys
from os.path import dirname, abspath
from datetime import datetime

from pymongo import MongoClient

sys.path.append(dirname(dirname(abspath(__file__))))

from jobs import app
from jobs.clean import clean_replica
from config import config_otc as _conf
from annou_otc.annou import OtcAnnouncement
from annou_otc.base import DataPopulation
from eggs.utils.log import logger


def annou_jobs():
    logger.info('Start Crawler OTC from Mongo!')
    OtcAnnouncement(1).extract()
    OtcAnnouncement(0).extract()
    logger.info('End Crawler OTC from Mongo!')


def update_secu_fields():
    logger.info('Start Update record from Mongo <{} {} {}>!'.format(_conf.DATA_HOST, _conf.DB_OTC, _conf.TABLE_OTC))

    db = MongoClient(_conf.DATA_HOST, _conf.PORT)
    collection = db[_conf.DB_OTC][_conf.TABLE_OTC]

    fields = {'secu': 1}
    query = {'sid': re.compile(r'http')}

    for docs in collection.find(query, fields):
        old_secu = docs['secu'][0]
        code = old_secu['cd'][:6]
        old_org = old_secu['org'].strip()

        if not old_org:
            new_secu = DataPopulation.other_secu(code)

            if new_secu[0]['org']:
                collection.update(
                    spec={'_id': docs['_id']},
                    document={'$set': {'stat': 2, 'upt': datetime.now(), 'secu': new_secu}}
                )
    db.close()
    logger.info('End Update record from Mongo <{} {} {}>!'.format(_conf.DATA_HOST, _conf.DB_OTC, _conf.TABLE_OTC))

app.add_job(annou_jobs, trigger='cron', hour='9-23', minute='*/20')
app.add_job(update_secu_fields, trigger='cron', hour='9-18', minute='*/30')
app.add_job(clean_replica, trigger='cron', hour='9-23', minute='*/20')
app.start()


