# -*- coding: utf-8 -*-
import re
import sys
from os.path import dirname, abspath
from datetime import datetime

from pymongo import MongoClient

sys.path.append(dirname(abspath(__file__)))

from jobs import app
from config import config_otc as _conf
from annou_otc.annou import OtcAnnouncement
from annou_otc.base import DataPopulation


def annou_jobs():
    OtcAnnouncement(1).extract()
    OtcAnnouncement(0).extract()


def update_secu_fields():
    db = MongoClient(_conf.DATA_HOST, _conf.PORT)
    collection = db[_conf.DB_OTC][_conf.TABLE_OTC]

    fields = {'secu': 1}
    query = {'sid': re.compile(r'http')}

    for docs in collection.find(query, fields):
        old_code = docs['secu']['cd'].strip()

        if not old_code.endswith('_QS_EQ'):
            new_secu = DataPopulation.other_secu(old_code)

            if new_secu['cd'].endswith('_QS_EQ'):
                collection.update(
                    spec={'_id': docs['_id']},
                    document={'$set': {'stat': 2, 'upt': datetime.now(), 'secu': new_secu}}
                )
    db.close()

app.add_job(annou_jobs, trigger='cron', hour='9-23', minute='*/20')
app.add_job(update_secu_fields, trigger='cron', hour='9-18', minute='*/30')
app.start()


