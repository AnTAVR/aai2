import logging
import os
import subprocess
from typing import Union

from libs.log import decor_log_debug

logger = logging.getLogger(__name__)


@decor_log_debug(logger)
def pacman(command: str, pkg: str = None,
           path_root: Union[str, bytes, os.PathLike] = None) -> int:
    """Запуск pacman с параметрами

    :param command:
    :param pkg:
    :param path_root:
    """
    _command = 'pacman'
    _command = [_command, command]
    if path_root is not None:
        _command.append('--root "{}"'.format(path_root))
    if pkg is not None:
        _command.append(pkg)

    return subprocess.call(_command)


@decor_log_debug(logger)
def yaourt(command: str, pkg: str = None,
           path_root: Union[str, bytes, os.PathLike] = None) -> int:
    """Запуск yaourt с параметрами

    :param command:
    :param pkg:
    :param path_root:
    """
    _command = 'yaourt'
    _command = [_command, command]
    if path_root is not None:
        _command.append('--root "{}"'.format(path_root))
    if pkg is not None:
        _command.append(pkg)

    return subprocess.call(_command)


class Pkg:
    inst_pkgs = []
    path_root: Union[str, bytes, os.PathLike] = None

    @classmethod
    def _install(cls, pkg: str, *, aur: bool = False) -> int:
        if aur:
            returncode = yaourt('-S', pkg, cls.path_root)
        else:
            returncode = pacman('-S', pkg, cls.path_root)
        if not returncode:
            cls.inst_pkgs.append(pkg)
        return returncode
