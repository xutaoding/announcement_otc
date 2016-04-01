# -*- coding: utf-8 -*-

import hashlib
import linecache
import os
import re
import sys
import time
import urllib2
from datetime import date, datetime
from random import sample
from string import digits, letters

import chardet
import pyPdf
from eggs.dbs import Mongodb

from eggs.utils.bucket import Bucket
from config.config_otc import ROOT_AWS_KEY
from config.config_otc import ROOT_PATH, PORT
from config.config_otc import DB_RULE, RULE_HOST, TABLE_RULE
from config.config_otc import STOCK_DB, STOCK_HOST, STOCK_TABLE


def error_info():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('Exception in:({}, LINE {} "{}") \n\tError: {}'.format(filename, lineno, line.strip(), exc_obj))


class BaseDownload(object):
    def get_html(self, url, data=None, encoding=False):
        for i in range(1, 5):
            req = urllib2.Request(url) if not data else urllib2.Request(url, data)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0')
            try:
                response = urllib2.urlopen(req, timeout=30.0)
                feed_data = response.read()
                response.close()
                if not encoding:
                    time.sleep(0.35)
                    return feed_data
                return self.to_utf8(feed_data)
            except Exception as e:
                print 'Web open error', i, 'times:', e
                time.sleep(40.0)
        return 'None'

    @staticmethod
    def to_utf8(string):
        charset = chardet.detect(string)['encoding']
        if charset is None:
            return string
        if charset != 'utf-8' and charset == 'GB2312':
            charset = 'gb18030'
        try:
            return string.decode(charset).encode('utf-8')
        except Exception, e:
            print 'chardet error:', e


class FileFiledInfo(BaseDownload):
    def __init__(self, title, file_url, file_ext):
        self.__title = title
        self.__file_url = file_url
        self.__file_ext = file_ext

    @property
    def aws(self):
        return Bucket()

    @property
    def aws_key(self):
        return ROOT_AWS_KEY + str(date.today()).replace('-', '') + '/'

    @property
    def file_pages(self):
        if self.__file_ext != 'pdf':
            return 1

        with open(self._storage_path, 'rb') as fp:
            pdf = pyPdf.PdfFileReader(fp)
            return pdf.getNumPages()

    @property
    def file_title(self):
        return self.__title

    @property
    def file_size(self):
        return os.path.getsize(self._storage_path)

    @staticmethod
    def encrypt_md5(source):
        if not isinstance(source, basestring):
            raise ValueError('md5 must string!')
        m = hashlib.md5()
        try:
            m.update(source)
        except UnicodeEncodeError:
            m.update(source.encode('u8'))
        return m.hexdigest()

    @property
    def filename(self):
        return self.encrypt_md5(self.file_title + self.__file_url)

    @property
    def file_ext(self):
        return self.__file_ext

    @property
    def abs_filename(self):
        return self.filename + '.' + self.file_ext

    @property
    def file_md5_value(self):
        with open(self._storage_path) as fp:
            return self.encrypt_md5(fp.read(200))

    @property
    def file_url(self):
        return '/' + ROOT_AWS_KEY + str(date.today()).replace('-', '') + '/'

    @property
    def file_src(self):
        return self.__file_url

    def compress_file(self):
        pass

    def _upload_s3(self):
        response = self.get_html(self.__file_url)
        self._storage_path = ROOT_PATH + self.abs_filename

        # Download html from web

        if self.__file_ext.lower() == 'pdf':
            with open(self._storage_path, 'wb') as fp:
                fp.write(response)
        else:
            # if ext is 'pdf', deal with on latter
            raise TypeError('ext: <{0}> is not pdf, Please handle it'.format(self.__file_ext))

        # Upload aws S3
        self.aws.put(self.aws_key + self.abs_filename, self._storage_path)

    @staticmethod
    def remove_files():
        root_path = ROOT_PATH

        for filename in os.listdir(root_path):
            os.remove(root_path + filename)

    def file_data(self):
        self._upload_s3()

        data = {
            'fn': self.filename, 'ext': self.file_ext, 'bytes': self.file_size,
            'pn': self.file_pages, 'md5': self.file_md5_value, 'url': self.file_url, 'src': self.file_src
        }

        self.remove_files()
        return data


class TypFieldIdentification(FileFiledInfo):
    def __init__(self, title, file_url, file_ext):
        self.__coll = Mongodb(RULE_HOST, PORT, DB_RULE, TABLE_RULE)
        super(TypFieldIdentification, self).__init__(title, file_url, file_ext)

    def __get_typ_filed(self, rule_type):
        rules_match = []
        sorted_fields = ('_id', 1)
        query = {'type': rule_type}
        fields = {'rule': 1, 'code': 1}

        count = 0
        for rule_dict in self.__coll.query(query, fields).sort([sorted_fields]):
            count += 1
            rule = rule_dict['rule']
            pattern = rule.replace('_', '.*?')
            pattern = pattern.replace('(', '.').replace(')', '.')
            if re.compile(r'%s' % pattern).search(self.file_title) is not None:
                rules_match.append((rule, rule_dict['code']))

        if rules_match:
            rules_match.sort(key=lambda s: len(s[0]), reverse=True)
            return rules_match[0][1]

    def get_typ(self):
        typ_field_value = self.__get_typ_filed(1)

        if typ_field_value is None:
            typ_field_value = self.__get_typ_filed(2)
        self.__coll.disconnect()
        return typ_field_value if typ_field_value else None


class CatFiledIdentification(FileFiledInfo):
    # def __init__(self, title, file_url, file_ext):
    #     super(CatFiledIdentification, self).__init__(title, file_url, file_ext)

    def __validation(self, basic_keywords, keyword, result):
        if keyword in self.file_title:
            for word in basic_keywords:
                if word in self.file_title:
                    break
            else:
                return result

    @property
    def annual_keywords(self):
        return {u'更正公告', u'更新后', u'已取消', u'披露日期的提示性公告'}

    def __semiannual_report(self):
        result = ['1030301']
        semiannual = u'半年度报告'

        return self.__validation(self.annual_keywords, semiannual, result)

    def __annual_report(self):
        result = ['1030101']
        annual = u'年度报告'

        return self.__validation(self.annual_keywords, annual, result)

    def __first_quarter_report(self):
        result = ['1030501']
        first_quarter = u'一季度报告'

        return self.__validation(self.annual_keywords, first_quarter, result)

    def __third_quarter_report(self):
        result = ['1030701']
        third_quarter = u'三季度报告'

        return self.__validation(self.annual_keywords, third_quarter, result)

    def __public_transfer_instruction(self):
        result = ['1020301']
        instructs = u'公开转让说明书'
        keywords = {u'更正公告', u'更正后'}

        return self.__validation(keywords, instructs, result)

    def __listed_public_transfer(self):
        # Open the transfer of the suggestive announcement
        result = ['10213']
        transfer_words = u'挂牌公开转让的提示性公告'

        return result if transfer_words in self.file_title else None

    def __shareholders_conference(self):
        result = ['119']
        shareholder_words = u'股东大会'

        return result if shareholder_words in self.file_title else None

    @staticmethod
    def __others():
        # 中关村股份报价转让公司
        return ['1010519']

    def get_cat(self):
        cat_value = self.__others()

        semiannual = self.__semiannual_report()
        annual = self.__annual_report()
        first_quarter = self.__first_quarter_report()
        third_quarter = self.__third_quarter_report()
        transfer_instruction = self.__public_transfer_instruction()
        listed_transfer = self.__listed_public_transfer()
        shareholder = self.__shareholders_conference()

        return semiannual or annual or first_quarter or third_quarter \
            or transfer_instruction or listed_transfer or shareholder or cat_value


class DataPopulation(TypFieldIdentification, CatFiledIdentification):
    def __init__(self, code, file_path, pub, title, file_ext, pdt):
        self.__code = code
        self.__pub = pub
        self.__pdt = pdt
        self.__src = file_path
        self.__coll_stock = Mongodb(STOCK_HOST, PORT, STOCK_DB, STOCK_TABLE)
        super(DataPopulation, self).__init__(title, file_path, file_ext)

    def other_secu(self, code):
        query = {'tick': code}
        fields = {'code': 1, 'org.id': 1, 'mkt.code': 1}
        secu = [{'cd': code, 'mkt': '', 'org': ''}]

        try:
            stock_dict = self.__coll_stock.get(query, fields)
            secu[0]['cd'] = stock_dict['code']
            secu[0]['mkt'] = stock_dict['mkt']['code']
            secu[0]['org'] = stock_dict['org']['id']
        except (KeyError, TypeError, IndexError):
            pass
        return secu

    @property
    def other_pub(self):
        return datetime.strptime(self.__pub, '%Y-%m-%d')

    @property
    def other_src(self):
        return self.__src

    @property
    def other_sid(self):
        return os.path.splitext(os.path.split(self.__src)[-1])[0]

    @property
    def random_characters(self):
        characters = sample(letters, 8) + sample(digits, 5) + sample(letters, 5)
        return ''.join(characters)

    @property
    def other_pid(self):
        timestamp_rand = str(time.time()) + self.random_characters
        return self.encrypt_md5(timestamp_rand)

    def _others_field(self):
        others = {
            'title': self.file_title, 'pid': self.other_pid, 'upt': datetime.now(), 'crt': datetime.now(),
            'src': self.other_src, 'sid': self.other_sid, 'pub': self.other_pub, 'secu': self.other_secu(self.__code),
            'cru': '000000', 'upu': '000000',  'valid': '1', 'stat': 2, 'effect': None, 'check': None,
            'audit': None
        }
        return others

    def populate_data(self):
        try:
            data = {}
            data.update(typ=self.get_typ())
            data.update(cat=self.get_cat())
            data.update(file=self.file_data())
            data.update(self._others_field())
            return data
        except Exception as e:
            error_info()
            print('Data Error: [{0}]'.format(e))

        self.__coll_stock.disconnect()
        return {}

