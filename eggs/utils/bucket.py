import ssl
import logging
import boto
from boto.s3 import connection
from os.path import abspath as _abs

from config import config_otc as config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Base(object):
    def __init__(self):
        self.__config = {k: getattr(config, k) for k in dir(config) if k[0].isupper()}

    @property
    def access_key(self):
        return self.__config['AWS_ACCESS_KEY_ID']

    @property
    def secret_key(self):
        return self.__config['AWS_SECRET_ACCESS_KEY']

    @property
    def host(self):
        return self.__config['AWS_HOST']

    @property
    def bucket_name(self):
        return self.__config['BUCKET_NAME']


class Bucket(Base):
    def __init__(self):
        super(Bucket, self).__init__()

        self.conn = boto.connect_s3(
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                host=self.host,
                calling_format=boto.s3.connection.OrdinaryCallingFormat(),
        )

    def all_buckets_name(self):
        return [bucket.name for bucket in self.conn.get_all_buckets()]

    def lookup(self):
        return self.conn.lookup(self.bucket_name)

    def get_buck(self):
        return self.conn.get_bucket(self.bucket_name)

    def create_bucket(self):
        pass

    def delete_bucket(self):
        pass

    def put(self, key_name, filename):
        """
        :param key_name: key name of Amazon S3
        :param filename: Store local directory filename path
        """
        try:
            bucket = self.get_buck()
            key = bucket.new_key(key_name)
            key.set_contents_from_filename(filename)
        except Exception as e:
            logger.info('Upload file to S3 error: type <{}>, msg <{}>, file <{}>'.format(
                e.__class__, e, _abs(__file__)))

    def get(self, key_name, filename=None):
        """
        :param key_name: key name of Amazon S3
        :param filename: Store local directory filename path
        :return `boto.s3.key.Key` class instance
        """
        try:
            bucket = self.get_buck()
            key = bucket.get_key(key_name)

            if key and filename is not None:
                key.get_contents_to_filename(filename)

            return key
        except ssl.SSLError as e:
            pass
            # logger.info('Get file from S3 error: type <{}>, msg <{}>, file <{}>'.format(
            #     e.__class__, e, _abs(__file__)))

    def list_keys(self, prefix=''):
        """
        List key from S3 bucket
        :param prefix: key part
        """
        try:
            bucket = self.get_buck()
            lister = bucket.list(prefix)

            for key in lister:
                yield key.name
        except ssl.SSLError:
            yield

    def delete_key(self):
        pass

    def close(self):
        return self.conn.close()

