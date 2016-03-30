import re

from announcement_otc.announcement import OtcAnnouncement
from config.config_otc import ANNOC_TYPE_ONE_DATE, ANNOC_TYPE_TWO_DATE


def validation(is_valid_date):
    pattern = re.compile(r'\d{4}-\d\d-\d\d')

    if pattern.search(is_valid_date) is None:
        raise ValueError("Date format Error, {} isn't excepted `0000-00-00` format".format(is_valid_date))


def run_otc_one_update():
    """ base type is 1 announcement for special date """
    for otc_one_date in ANNOC_TYPE_ONE_DATE:
        validation(otc_one_date)
        OtcAnnouncement(1, otc_one_date, otc_one_date).extract()


def run_otc_two_update():
    """ base type is 2 announcement for special date """
    for otc_two_date in ANNOC_TYPE_TWO_DATE:
        validation(otc_two_date)
        OtcAnnouncement(2, otc_two_date, otc_two_date).extract()


if __name__ == '__main__':
    OtcAnnouncement(1).extract()
    # run_otc_one_update()
    # run_otc_two_update()
