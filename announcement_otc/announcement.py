# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
from datetime import date

import simplejson

from base import DataPopulation, BaseDownload
from config.config_otc import URI, PORT, DATA_HOST, DB_OTC, TABLE_OTC, CRT_INDEX
from eggs.dbs import Mongodb


class OtcAnnouncement(BaseDownload):
    def __init__(self, typ=1, start_date=None, end_date=None):
        self._typ = typ

        if (start_date and not end_date) or (not start_date and end_date):
            raise ValueError('Arguments error.')

        if start_date is None and end_date is None:
            self._start_date = self._end_date = str(date.today())
        else:
            self._start_date = start_date
            self._end_date = end_date
        self._base_url = URI.format(self._typ, self._start_date, self._end_date, '{0}')
        self._coll = Mongodb(DATA_HOST, PORT, DB_OTC, TABLE_OTC)

    def crawl_info(self):
        current_pages = 1
        total_pages = 2
        switch_pages = False

        result_infos = []
        keys = ['companyCode', 'filePath', 'publishDateString', 'title', 'fileExt', 'uploadDateTime']

        while current_pages <= total_pages:
            # print self._base_url.format(current_pages)
            json_data = self.get_html(self._base_url.format(current_pages))
            py_objects = simplejson.loads(json_data)

            if not switch_pages:
                page_size = py_objects['pagingInfo']['pageSize']
                total_count = py_objects['pagingInfo']['totalCount']
                integer, remainder = divmod(total_count, page_size)
                total_pages = integer + (remainder and 1)
                switch_pages = True

            for info in py_objects['disclosureInfos']:
                each_info = []
                for key in keys:
                    if key == 'filePath':
                        each_info.append('http://file.neeq.com.cn/upload' + info[key])
                    else:
                        each_info.append(info[key])
                result_infos.append(each_info)

            print('Page: {0} done! Sleeping {1}s'.format(current_pages, 5))
            time.sleep(5)
            current_pages += 1
            break
        return result_infos

    def create_index(self, unique_id=None):
        if unique_id is not None:
            try:
                json_resp = self.get_html(CRT_INDEX)
                if simplejson.loads(json_resp)['code'] == 200:
                    print('\tCreate index ok!\n\n')
            except Exception as e:
                print('create index error: [{0}]'.format(e.message))

    def extract(self):
        items_info = self.crawl_info()

        for k, item in enumerate(items_info):
            code, file_path, pub, title, file_ext, pdt = item
            data = DataPopulation(code, file_path, pub, title, file_ext, pdt).populate_data()

            if data or not self._coll.get({'sid': file_path}, {'sid': 1}):
                current_id = self._coll.insert(data)
                message = 'typ: {0} k: {1} mongo id: {6}, code: {5} pub: {3} title: {2} \n\tfile_url: {4}'
                print(message.format(self._typ, k + 1, title, pub, file_path, code, current_id))

                # self.create_index(current_id)
        self._coll.disconnect()

