import functools
import logging
import os
from typing import Union

logger = logging.getLogger(__name__)


def logging_init(loglevel: Union[int, str], log_file: Union[str, bytes, os.PathLike] = None):
    if log_file is None:
        handler = logging.StreamHandler()
    else:
        handler = logging.FileHandler(log_file, 'w')
    format_ = "%(levelname)s:%(name)s:%(lineno)s  %(message)s"
    # format_ = "[%(filename)s:%(lineno)s - %(funcName)s()] %(message)s"
    formatter = logging.Formatter(format_)
    # formatter = logging.Formatter(logging.BASIC_FORMAT)
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)
    # try:
    #     # noinspection PyUnresolvedReferences
    #     import colorlog
    #
    #     colorlog.basicConfig()
    #     del colorlog
    # except ImportError as err:
    #     logger.warning(err)

    logging.root.setLevel(loglevel)


def decor_log_debug(logger_: logging.Logger, run: bool = False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ret = None
            logger_.log(logging.DEBUG,
                        '{}:{}({!r}, {!r})'.format(func.__code__.co_firstlineno,
                                                   func.__code__.co_name,
                                                   args, kwargs, ret))
            if logging.root.level != logging.DEBUG or run:
                ret = func(*args, **kwargs)
            # noinspection PyUnresolvedReferences
            logger_.log(logging.DEBUG,
                        '{}:{}()->{!r}'.format(func.__code__.co_firstlineno,
                                               func.__code__.co_name,
                                               ret))
            return ret

        return wrapper

    return decorator


class DebugFileProxy:
    @staticmethod
    def write(val):
        logger.debug(val)

    @staticmethod
    def flush():
        pass
