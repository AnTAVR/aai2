import logging
from gettext import gettext as _
from typing import List, Tuple

from aai_framework.dial import ColorTxt
from aai_framework.interface import ModuleInterface, DialogTestInterface
from libs.net import is_ipv4, is_ipv6
from .l_connector import ConnectorBase
from .main import vars_, Vars, Options, Connector

logger = logging.getLogger(__name__)


# noinspection PyAbstractClass
class ModuleStrategyBase(ModuleInterface):
    opti_: Options = None
    OptionsClass = Options
    _connector: Connector = None
    ConnectorClass = ConnectorBase

    @property
    def vars_(self) -> Vars:
        return vars_

    def __init__(self):
        super().__init__()
        self.opti_ = self.OptionsClass()

    @property
    def connector(self) -> ConnectorBase:
        if self._connector is None:
            self._connector = self.ConnectorClass(self.opti_)
        # noinspection PyTypeChecker
        return self._connector


# noinspection PyAbstractClass
class ModuleStrategyNetBase(ModuleStrategyBase, DialogTestInterface):
    def __init__(self, iface: str):
        super().__init__()
        self.opti_.iface = iface

    def _head_txt(self, help_txt_new: List[str] = None, all_: bool = False) -> List[str]:
        tmp = [
            (_('сетевой адаптер ({}): {}'), 'iface', self.opti_.iface, all_),
            (_('DNS сервер ({}): {}'), 'dns', self.opti_.dns, all_),
            (_('прокси сервер ({}): {}'), 'http_proxy', self.opti_.http_proxy, all_),
            (_('прокси сервер ({}): {}'), 'https_proxy', self.opti_.https_proxy, all_),
            (_('прокси сервер ({}): {}'), 'ftp_proxy', self.opti_.ftp_proxy, all_),
        ]
        help_txt = self.format_head_txt(tmp)

        if help_txt_new is not None:
            help_txt = help_txt_new + help_txt

        return help_txt

    def test_dns(self, val: str) -> bool:
        if is_ipv4(val) if self.opti_.ipv4 else is_ipv6(val):
            return True

        text_err: str = _('Не правильный DNS сервер ({})').format(val)

        self._dialog_err(text_err)
        return False

    def dialog_dns(self, test_: bool = False) -> Tuple[str, str]:
        key = 'dns'

        default = '8.8.8.8' if self.opti_.ipv4 else '2001:4860:4860::8888'

        demo_text = 'google DNS: '
        demo_text += default
        demo_text = ColorTxt(demo_text).blue.bold

        help_txt = self._head_txt()
        help_txt += ['', _('Введите DNS сервер ({})').format(key),
                     demo_text]

        if self.opti_.address is None:
            default = ''

        while True:
            code, value = self._dialog_inputbox(default, help_txt)  # type: str str
            if code in self.my_dialog.ESC_CANCEL:
                return code, value
            if not test_ and not value:
                return code, value
            if self.test_dns(value):
                return code, value
            default = value

    # def dialog_http_proxy(self) -> Tuple[str, str]:
    #     key = 'http_proxy'
    #
    #     demo_text = 'http://user:password@server:port/'
    #     demo_text = ColorTxt(demo_text).blue.bold
    #
    #     default = ''
    #
    #     help_txt = self._head_txt()
    #     help_txt += ['', _('Введите {0} прокси сервер ({0})').format(key),
    #                  demo_text]
    #
    #     return self._dialog_inputbox(default, help_txt)
    #
    # def dialog_https_proxy(self) -> Tuple[str, str]:
    #     key = 'https_proxy'
    #
    #     demo_text = 'https://user:password@server:port/'
    #     demo_text = ColorTxt(demo_text).blue.bold
    #
    #     default = ''
    #
    #     help_txt = self._head_txt()
    #     help_txt += ['', _('Введите {0} прокси сервер ({0})').format(key),
    #                  demo_text]
    #
    #     return self._dialog_inputbox(default, help_txt)
    #
    # def dialog_ftp_proxy(self) -> Tuple[str, str]:
    #     key = 'ftp_proxy'
    #
    #     demo_text = 'ftp://user:password@server:port/'
    #     demo_text = ColorTxt(demo_text).blue.bold
    #
    #     default = ''
    #
    #     help_txt = self._head_txt()
    #     help_txt += ['', _('Введите {0} прокси сервер ({0})').format(key),
    #                  demo_text]
    #
    #     return self._dialog_inputbox(default, help_txt)

    def dialog_proxy(self) -> Tuple[str, List[str]]:
        demo_text = 'protocol://user:password@server:port/'
        demo_text = ColorTxt(demo_text).blue.bold

        help_txt = self._head_txt()
        help_txt += ['', _('Введите прокси сервера'),
                     demo_text]

        help_txt = '\n'.join(help_txt)

        title_column = 1
        field_column = 15
        field_length = 45
        input_length = 120
        elements = (
            # title, title_row, title_column, field, field_row, field_column, field_length, input_length
            ('http_proxy', 1, title_column, '', 1, field_column, field_length, input_length),
            ('https_proxy', 3, title_column, '', 3, field_column, field_length, input_length),
            ('ftp_proxy', 5, title_column, '', 5, field_column, field_length, input_length),
        )
        return self.my_dialog.form(help_txt, elements, 20, 70, 5, title=self.name)

    def run_all(self) -> bool:
        # code, value = self.dialog_http_proxy()
        # if code in self.my_dialog.ESC_CANCEL:
        #     return False
        # self.opti_.http_proxy = value or self.opti_.__class__.http_proxy
        #
        # code, value = self.dialog_https_proxy()
        # if code in self.my_dialog.ESC_CANCEL:
        #     return False
        # self.opti_.https_proxy = value or self.opti_.__class__.https_proxy
        #
        # code, value = self.dialog_ftp_proxy()
        # if code in self.my_dialog.ESC_CANCEL:
        #     return False
        # self.opti_.ftp_proxy = value or self.opti_.__class__.ftp_proxy

        code, values = self.dialog_proxy()
        if code in self.my_dialog.ESC_CANCEL:
            return False

        self.opti_.http_proxy = values[0] or self.opti_.__class__.http_proxy
        self.opti_.https_proxy = values[1] or self.opti_.__class__.https_proxy
        self.opti_.ftp_proxy = values[2] or self.opti_.__class__.ftp_proxy

        code = self.dialog_test()
        if code == self.my_dialog.OK:
            return True
