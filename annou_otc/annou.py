# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import urllib
from datetime import date, datetime, timedelta

import simplejson

from base import DataPopulation
from config.config_otc import URI, PORT, DATA_HOST, DB_OTC, TABLE_OTC, CRT_INDEX, FORM_DATA
from eggs.dbs import Mongodb
from eggs.utils.utils import md5
from eggs.utils.loader import BaseDownload


class OtcAnnouncement(BaseDownload):
    annou_typ = {1: '新三板', 0: '老三板'}

    def __init__(self, typ=1, start_date=None, end_date=None, code=''):
        """
        该类主要抓取 http://www.neeq.com.cn/disclosure/announcement.html 网站上，老三板和新三板的公司公告

        :param typ: 三板公告类型， 0是老三板， 1是新三板
        :param start_date: 抓取的起始时间, 0000-00-00
        :param end_date: 抓取的结束时间, 0000-00-00
        :code: string: 格式位000000或空
        """
        assert int(typ) in [0, 1]
        self._typ = int(typ)
        self._code = code

        if (start_date and not end_date) or (not start_date and end_date):
            raise ValueError('Arguments error.')

        if start_date is None and end_date is None:
            self._start_date = str(date.today() - timedelta(days=1))
            self._end_date = str(date.today())
        else:
            self._start_date = start_date
            self._end_date = end_date

        self._base_url = URI
        self._form_data = self.form_data

        self._switch = False
        self._total_pages = 1
        self._coll = Mongodb(DATA_HOST, PORT, DB_OTC, TABLE_OTC)
        self._seen = self.seen

    @property
    def form_data(self):
        _form_data = FORM_DATA.copy()

        _form_data['isNewThree'] = self._typ
        _form_data['startTime'] = self._start_date
        _form_data['endTime'] = self._end_date
        _form_data['companyCd'] = self._code
        return _form_data

    def create_index(self, unique_id=None):
        if unique_id is not None:
            try:
                json_resp = self.get_html(CRT_INDEX)
                if simplejson.loads(json_resp)['code'] == 200:
                    print('\tCreate index ok!\n\n')
            except Exception as e:
                print('create index error: [{0}]'.format(e.message))

    @property
    def seen(self):
        key = 'sid'
        fields = {key: 1}
        query = {
            'pdt':
                {
                    '$gte': datetime.strptime(self._start_date, '%Y-%m-%d'),
                    '$lte': datetime.strptime(self._end_date, '%Y-%m-%d')
                },
            'sid': re.compile(r'http')
        }

        if self._code:
            query['secu.cd'] = re.compile(r'%s' % self._code)

        return {md5(docs['sid']) for docs in self._coll.query(query, fields)}

    def crawl_info(self, page=0):
        result_infos = []
        keys = ['companyCd', 'destFilePath', 'publishDate', 'disclosureTitle', 'fileExt', 'upDate']

        self._form_data['page'] = str(page)
        json_data = self.get_html(self._base_url, urllib.urlencode(self._form_data))
        py_objects = simplejson.loads(json_data[2:-2])
        required_data = py_objects['listInfo']

        if not self._switch:
            self._switch = True
            self._total_pages = required_data['totalPages']

        for info in required_data['content']:
            each_info = []
            for key in keys:
                if key == 'destFilePath':
                    each_info.append('http://www.neeq.com.cn' + info[key])
                elif key == 'upDate':
                    each_info.append(info[key]['time'])
                else:
                    each_info.append(info[key])
            result_infos.append(each_info)

        return result_infos

    def process(self, items):
        """
        由['companyCd', 'destFilePath', 'publishDate', 'disclosureTitle', 'fileExt', 'upDate']字段值组成的列表
        :param items: list of  seven item list
        :return:
        """
        for k, item in enumerate(items):
            code, file_path, pub, title, file_ext, pdt = item

            # 必须先过滤， 后下载文件和计算
            url_md5 = md5(file_path)
            if url_md5 not in self.seen:
                data = DataPopulation(code, file_path, pub, title, file_ext, pdt).populate_data()

                if data:
                    self._seen.add(url_md5)
                    current_id = self._coll.insert(data)

                    # 在上海环境跑程序， 不用建立索引
                    # self.create_index(current_id)
                    message = 'typ: {0} k: {1} mongo id: {6}, code: {5} pub: {3} title: {2} \n\tfile_url: {4}\n'
                    print(message.format(self.annou_typ[self._typ], k + 1, title, pub, file_path, code, current_id))

    def extract(self):
        self.process(self.crawl_info())

        for page in range(1, self._total_pages + 1):
            self.process(self.crawl_info(page))
        self._coll.disconnect()

        DataPopulation.close()


if __name__ == '__main__':
    dt = '2016-04-14'
    OtcAnnouncement(typ=1, start_date=dt, end_date=dt).extract()

