import os
import subprocess
from typing import Union

from libs import systemd


def timesyncd(command: str, path_root: Union[str, bytes, os.PathLike] = '') -> subprocess.CompletedProcess:
    """Работа с сервисом синхронизации времени

    :param command: enable | disable | start
    :param path_root:
    """
    return systemd.systemctl(command, 'systemd-timesyncd.service', path_root)
