# -*- coding: utf-8 -*-
import os
import sys
from os.path import dirname, abspath

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

sys.path.append(dirname(abspath(__file__)))

from annou_otc.annou import OtcAnnouncement


def create_sqlite():
    sqlite_path = dirname(abspath(__file__))
    for sql_path in os.listdir(sqlite_path):
        if sql_path.endswith('.db'):
            os.remove(os.path.join(sqlite_path, sql_path))

create_sqlite()


jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.db')
}

# using ThreadPoolExecutor as default other than ProcessPoolExecutor(not work) to executors
executors = {
    # 'default': ThreadPoolExecutor(4),
    'default': ProcessPoolExecutor(4),
}

job_defaults = {
    'coalesce': False,
    'max_instances': 1
}


def annou_jobs():
    OtcAnnouncement(1).extract()
    OtcAnnouncement(0).extract()

app = BlockingScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)

app.add_job(annou_jobs, trigger='cron', hour='9-23', minute='*/15')
app.start()


