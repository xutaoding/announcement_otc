# -*- coding: utf-8 -*-

import pymongo
import pymongo.errors


class Mongodb(object):
    def __init__(self, host, port, database, collection):
        self.__host = host
        self.__port = port
        self.__db_name = database
        self.__coll_name = collection
        self.__conn = None

    def __connect(self):
        if self.__conn is not None:
            self.__conn.close()
        try:
            self.__conn = pymongo.MongoClient(self.__host, self.__port)
            self.__db = self.__conn[self.__db_name]
            self.__collection = self.__db[self.__coll_name]
        except Exception, e:
            print 'connect update_ error:', e

    def disconnect(self):
        try:
            if self.__conn is not None:
                self.__conn.close()
        except Exception, e:
            print 'close update_ error:', e
        finally:
            self.__conn = None

    def get_db(self):
        if self.__conn is None:
            self.__connect()
        return self.__db

    def count(self, condition=None):
        if self.__conn is None:
            self.__connect()

        try:
            if condition is None:
                return self.__collection.count()

            if not isinstance(condition, dict):
                raise ValueError('`condition` is not dict type.')
            return self.query(condition).count()
        except Exception, e:
            print 'count error:', e

    def get(self, condition, kwargs=None, spec_sort=None):
        """
        `type(condition) is not dict` or `type(condition) == dict` is all right.
        condition is `spec_or_id` parameter of find_one function in pymongo
        """
        if not isinstance(condition, dict):
            raise TypeError('condition type error in get')
        if not isinstance(kwargs, (dict, type(None))):
                raise TypeError('`kwargs` fields type error.')

        if self.__conn is None:
            self.__connect()

        if kwargs is None and spec_sort is None:
            # `**{}` is dict in function parameter, also `fine_one` function `kwargs` parameter
            return self.__collection.find_one(condition)
        if kwargs and spec_sort is None:
            return self.__collection.find_one(condition, kwargs)

        if spec_sort and not isinstance(spec_sort, tuple):
            #  `_sort` type apply to python of win OS, maybe other OS isn't tuple
            raise TypeError('`sort` is empty or Type error.')

        if kwargs is None:
            return self.__collection.find(condition).sort([spec_sort]).limit(-1)[0]
        elif kwargs:
            return self.__collection.find(condition, kwargs).sort([spec_sort]).limit(-1)[0]

    def query(self, condition=None, kwargs=None):
        if condition is None:
            condition = dict()

        if not isinstance(condition, dict):
            raise TypeError('condition type error in query')
        if not isinstance(kwargs, (dict, type(None))):
            raise TypeError('`kwargs` type error in query')

        if self.__conn is None:
            self.__connect()
        if kwargs is None:
            return self.__collection.find(condition, **{})
        elif kwargs:
            return self.__collection.find(condition, kwargs)

    def insert(self, data, batch=None):
        """
        data: eg, {...}, or [{...}, {...}, ...]
        """
        if self.__conn is None:
            self.__connect()

        try:
            return self.__collection.insert(data)
        except Exception, e:
            print 'insert signal data error:', e

    def update(self, condition, setdata=None, unset_keys=None):
        """
       condition: indicate that get must a unique record in __collection.
       if not, only update_ one record, others can not update_.
        """
        if not isinstance(condition, dict):
            raise TypeError('condition type error in update_')

        if not isinstance(unset_keys, (list, tuple, type(None))):
            raise TypeError('`unset_keys` is tuple or list of string.')

        if self.__conn is None:
            self.__connect()
        try:
            # # $set 修改文档里已有字段或新增一个新字段
            if setdata is not None:
                self.__collection.update(condition, {'$set': setdata})

            #  # $unset 删除一个字段，unsetdata 为字段对应值
            if unset_keys is not None:
                self.__collection.update(condition, {'$unset': {k: True for k in unset_keys}})
        except Exception, e:
            print 'update error:', e

    def distinct(self, key=None):
        if key is None:
            raise ValueError('key is None Error')

        if self.__conn is None:
            self.__connect()
        try:
            return self.__collection.distinct(key)
        except Exception, e:
            print 'distinct error:', e

    def remove(self, condition):
        """
            if condition is {}, then drop all the data of this collection, but this collection
            itself isn't dropped; otherwise remove qualified data.
        """
        if type(condition) is not dict:
            raise TypeError('condition type error in remove')

        if self.__conn is None:
            self.__connect()
        try:
            return self.__collection.remove(condition)
        except Exception, e:
            print 'remove error:', e


if __name__ == '__main__':
    # coll_in = Mongodb('192.168.251.70', 27017, 'news', 'research_report_def')
    db = pymongo.MongoClient('192.168.251.70', 27017)
    print db.database_names()
