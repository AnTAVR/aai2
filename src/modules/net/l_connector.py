import logging
import os
import time
from gettext import gettext as _
from typing import List

import modules.main
from aai_framework.dial import ColorTxt
from aai_framework.interface import ModuleInterface
from libs.log import decor_log_debug
from libs.net import set_proxy
from libs.systemd import networkctl, systemctl
from libs.utils import remove, replace, symlink
from vendor.parser.unit import Unit, Comment, Section, Option
from .main import Connector

logger = logging.getLogger(__name__)


# noinspection PyAbstractClass
class ConnectorBase(Connector):
    RESOLV_CONF = 'resolv.conf'
    ROOT_RESOLV_DIR = 'etc'
    SYSTEMD_RESOLV_DIR = 'run/systemd/resolve'
    CONFIGURED_TIMEOUT = 60

    def dialog_configured(self) -> bool:
        help_txt: List[str] = [_('Подождите...'), '', '*' * 30]

        sec = 0

        ModuleInterface.my_dialog.gauge_start('\n'.join(help_txt), percent=sec)

        while sec < self.CONFIGURED_TIMEOUT:
            ret = networkctl('list', self.opti_.iface)
            if ret.returncode:
                return True
            ret = ret.stdout.decode()
            ret = ret.split()
            if ret[4] == 'configured':
                return True
            elif ret[4] == 'configuring':
                ret[4] = ColorTxt(ret[4]).yellow.bold
            else:
                ret[4] = ColorTxt(ret[4]).red.bold

            help_txt[2] = ' '.join(ret)

            ModuleInterface.my_dialog.gauge_update(int(sec / self.CONFIGURED_TIMEOUT * 100), '\n'.join(help_txt), True)

            time.sleep(1)
            sec += 1

        ModuleInterface.my_dialog.gauge_stop()
        return False

    def base_gen_systemd_network(self) -> Unit:
        unit = Unit()
        section = unit.get()
        section.append(Comment('This file is created by {}.'.format(modules.main.vars_.config.prog_name)))

        section = Section('Match')
        section.append(Option('Name', [self.opti_.iface]))
        unit.append(section)

        section = Section('Network')
        if self.opti_.dns is not None:
            section.append(Option('DNS', [self.opti_.dns]))
        unit.append(section)

        return unit

    @decor_log_debug(logger, True)
    def base_on(self, root: str = '/', ):
        if root == '/':
            systemctl('start', 'systemd-resolved', root)
        else:
            systemctl('enable', 'systemd-resolved', root)

        file_resolv = os.path.abspath(os.path.join(root, self.ROOT_RESOLV_DIR, self.RESOLV_CONF))
        file_resolv_bak = file_resolv + '.bak'
        file_resolv_systemd = os.path.abspath(os.path.join(root, self.SYSTEMD_RESOLV_DIR, self.RESOLV_CONF))

        remove(file_resolv_bak)
        replace(file_resolv, file_resolv_bak)
        symlink(file_resolv_systemd, file_resolv)

        set_proxy('http_proxy', self.opti_.http_proxy, root)
        set_proxy('https_proxy', self.opti_.https_proxy, root)
        set_proxy('ftp_proxy', self.opti_.ftp_proxy, root)

    @decor_log_debug(logger, True)
    def base_off(self, root: str = '/'):
        if root == '/':
            systemctl('stop', 'systemd-resolved', root)
        else:
            systemctl('disable', 'systemd-resolved', root)

        file_resolv = os.path.abspath(os.path.join(root, self.ROOT_RESOLV_DIR, self.RESOLV_CONF))
        file_resolv_bak = file_resolv + '.bak'

        replace(file_resolv_bak, file_resolv)

        set_proxy('http_proxy', '', root)
        set_proxy('https_proxy', '', root)
        set_proxy('ftp_proxy', '', root)
