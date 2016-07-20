# -*- coding: utf-8 -*-
import time
import urllib2
import chardet


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
                time.sleep(5)
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
