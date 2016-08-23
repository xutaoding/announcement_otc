import os
import logging
from logging.handlers import RotatingFileHandler
from os.path import join, dirname, abspath, exists


def get_logger(to_console=True, to_file=False):
    log_path = join(dirname(dirname(dirname(abspath(__file__)))), 'log')

    if not exists(log_path):
        os.makedirs(log_path)
    filename = join(log_path, 'job.log')

    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.INFO)

    if to_console:
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter('[%(asctime)s %(levelname)s]: %(message)s'))

        _logger.addHandler(console)

    if to_file:
        # RotatingFileHandler need parameters
        file_handler = RotatingFileHandler(filename, backupCount=10, maxBytes=5 * 1024 * 1024)
        file_handler.setLevel(logging.DEBUG)

        datefmt = '%Y-%m-%d %H:%M:%S'
        formatter = '[%(asctime)s %(levelname)s]: %(message)s'
        formatter = logging.Formatter(formatter, datefmt)
        file_handler.setFormatter(formatter)

        _logger.addHandler(file_handler)
    return _logger

logger = get_logger(to_console=False, to_file=True)

