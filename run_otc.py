# -*- coding: utf-8 -*-
import re
import sys
from datetime import timedelta, date

from annou_otc.annou import OtcAnnouncement


def validation(is_valid_date):
    pattern = re.compile(r'\d{4}-\d\d-\d\d')

    if pattern.search(is_valid_date) is None:
        raise ValueError("Date format Error, {} isn't excepted `0000-00-00` format".format(is_valid_date))


def get_date_range(start, end=None):
    """
    calculate date range
    :param start: string, yyyy-mm-dd, start date
    :param end: string, yyyy-mm-dd, end date
    :return: list, date string range list
    """
    date_range = []
    start = start.replace('-', '')
    end = end.replace('-', '') if end else start
    split_ymd = (lambda _d: (int(_d[:4]), int(_d[4:6]), int(_d[6:8])))
    date_start = date(*split_ymd(start))
    date_end = date(*split_ymd(end))

    while date_start <= date_end:
        date_range.append(str(date_start))
        date_start = timedelta(days=1) + date_start
    return date_range


def annou_otc_update(start, end):
    """
    新三板或老三板补抓
    :param typ: 公告类型，0是老三板，1是新三板
    :param start: 公告抓取开始时间
    :param end: 公告抓取结束时间
    :return:
    """
    validation(start)
    validation(end)

    date_range = get_date_range(start, end)
    start_dt, end_dt = date_range[0], date_range[-1]
    OtcAnnouncement(1, start_dt, end_dt).extract()
    OtcAnnouncement(0, start_dt, end_dt).extract()


if __name__ == '__main__':
    # 为防止漏抓，增加日期
    ANNOC_DATE = {
        'start': '2016-04-01',
        'end': '2016-07-19',
    }

    annou_otc_update(**ANNOC_DATE)
