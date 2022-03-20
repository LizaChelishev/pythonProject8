import logging
from configparser import ConfigParser
import threading


class Logger:
    instance = None
    lock = threading.Lock()

    config = ConfigParser()
    config.read("config.conf")
    LOG_LEVEL = config["logging"]["level"]
    LOG_FILE_NAME_PREFIX = config["logging"]["logfile_name_prefix"]
    LOG_FILE_NAME_EXT = config["logging"]["logfile_name_ext"]

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def get_instance(cls):
        if cls.instance:
            return cls.instance
        with cls.lock:
            if cls.instance is None:
                cls.instance = cls.__new__(cls)
                for handler in logging.root.handlers:
                    logging.root.removeHandler(handler)
                cls.instance.logger = logging.getLogger(__name__)
                cls.instance.logger.setLevel(logging.__dict__[cls.LOG_LEVEL])
                cls.instance.formatter = logging.Formatter(
                    f'%(asctime)s:%(module)s:%(funcName)s:%(process)d:%(thread)d:%(levelname)s:%(message)s')
                cls.instance.file_handler = logging.FileHandler(
                    f'{Logger.LOG_FILE_NAME_PREFIX}.{Logger.LOG_FILE_NAME_EXT}')
                cls.instance.file_handler.setLevel(logging.__dict__[cls.LOG_LEVEL])
                cls.instance.file_handler.setFormatter(cls.instance.formatter)
                cls.instance.logger.addHandler(cls.instance.file_handler)

                return cls.instance
            else:
                return cls.instance
