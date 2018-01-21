import logging
import os
import subprocess
from typing import Union

from libs.log import decor_log_debug

logger = logging.getLogger(__name__)


@decor_log_debug(logger)
def systemctl(command: str, unit: str, path_root: Union[str, bytes, os.PathLike] = '') -> subprocess.CompletedProcess:
    """Запуск systemctl с параметрами

    :param command: enable | disable | start
    :param unit:
    :param path_root:
    """
    _command = ['systemctl']
    if path_root and path_root != '/':
        _command.append('--root="{}"'.format(path_root))
    _command.append(command)
    _command.append(unit)

    return subprocess.run(_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def networkctl(command: str, iface: str = None) -> subprocess.CompletedProcess:
    """Запуск networkctl с параметрами

    :param command: list | status
    :param iface:
    """
    _command = ['networkctl', '--no-pager', '--no-legend', command]
    if iface is not None:
        _command.append(iface)
    return subprocess.run(_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
