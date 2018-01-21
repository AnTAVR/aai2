import logging
import os
import subprocess
from typing import Union

from libs.log import decor_log_debug

logger = logging.getLogger(__name__)


@decor_log_debug(logger)
def remove(path: Union[str, bytes, os.PathLike]):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


@decor_log_debug(logger)
def replace(path1: Union[str, bytes, os.PathLike], path2: Union[str, bytes, os.PathLike]):
    try:
        os.replace(path1, path2)
    except FileNotFoundError:
        pass


@decor_log_debug(logger)
def symlink(path1: Union[str, bytes, os.PathLike], path2: Union[str, bytes, os.PathLike]):
    try:
        os.symlink(path1, path2)
    except FileNotFoundError:
        pass


def is_bios_sys() -> bool:
    _command = ['efivar', '-l']
    try:
        ret = subprocess.run(_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        return True

    if ret.returncode != 0:
        return True

    return False
