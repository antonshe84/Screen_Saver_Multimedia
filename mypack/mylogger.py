import logging
import sys
from logging.handlers import TimedRotatingFileHandler


FORMATTER = logging.Formatter(u'%(filename)s [LINE:%(lineno)4d] %(levelname)-8s [%(asctime)s]  %(message)s')


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler(logger_file):
    file_handler = logging.FileHandler(logger_file)
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name, logger_file):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG) # лучше иметь больше логов, чем их нехватку
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler(logger_file))
    logger.propagate = False
    return logger