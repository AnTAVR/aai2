import logging
from gettext import gettext as _
from typing import Tuple, List

from aai_framework.dial import ColorTxt
from aai_framework.interface import ModuleInterface, DialogTestInterface
from libs.db import DbDomains, DbTimezones, DbLocales, DbKeymaps, DbFonts, DbFontMaps, DbFontUnimaps
from libs.pacman import Pkg
from .l_base import MirrorList
from .main import vars_, Options, Vars

logger = logging.getLogger(__name__)


class BaseGroupPkg(Pkg):
    @classmethod
    def install(cls):
        return


class Module(ModuleInterface, DialogTestInterface):
    ID = 'base'
    LEN_INSTALL = 1165

    opti_: Options = None

    DEFAULT_COUNTRY = 'RU'
    DEFAULT_ITEM = 'none'

    @property
    def vars_(self) -> Vars:
        return vars_

    def __init__(self):
        super().__init__()
        self.opti_ = Options()
        self.conflicts.add(self)

    @property
    def is_run(self) -> bool:
        return self.vars_.is_ok

    def _head_txt(self, help_txt_new: List[str] = None, all_: bool = False) -> List[str]:
        tmp = [
            (_('домен ({}): {}'), 'country', self.opti_.country, all_),
            (_('часовой пояс ({}): {}'), 'timezone', self.opti_.timezone, all_),
            (_('localtime ({}): {}'), 'localtime', self.opti_.localtime, all_),
            (_('локаль ({}): {}'), 'locale', self.opti_.locale, all_),
            (_('раскладка клавиатуры ({}): {}'), 'keymap', self.opti_.keymap, all_),
            (_('доп. раскладка клавиатуры ({}): {}'), 'keymap_toggle', self.opti_.keymap_toggle, False),
            (_('Шрифт ({}): {}'), 'font', self.opti_.font, all_),
            (_('карта шрифта ({}): {}'), 'font_map', self.opti_.font_map, False),
            (_('unicode карта шрифта ({}): {}'), 'font_unimap', self.opti_.font_unimap, False),
            (_('имя компьютера ({}): {}'), 'hostname', self.opti_.hostname, all_),
            (_('mirrorlist ({}): {}'), 'mirrorlist', self.opti_.mirrorlist, all_),
        ]
        help_txt = self.format_head_txt(tmp)

        if help_txt_new is not None:
            help_txt = help_txt_new + help_txt

        return help_txt

    @property
    def name(self) -> str:
        return _('Базовая система')

    @property
    def menu_item(self) -> Tuple[str, str]:
        text = [ColorTxt('(' + _('ВЫПОЛНЕНО') + ')').green.bold if self.is_run else
                ColorTxt('(' + _('ОБЯЗАТЕЛЬНО!!!') + ')').red.bold]

        return super().get_menu_item(text)

    def dialog_country(self) -> Tuple[str, str]:
        domains = DbDomains().read()

        items = domains.menu_items

        help_txt = self._head_txt()
        help_txt += ['', _('Выберите домен вашей страны')]

        default = self.opti_.country or self.DEFAULT_COUNTRY

        return self._dialog_menu(items, default, help_txt)

    def dialog_timezone(self) -> Tuple[str, str]:
        domains = DbDomains().read()
        timezones = DbTimezones().read()

        items = timezones.menu_items

        help_txt = self._head_txt()
        help_txt += ['', _('Выберите часовой пояс')]

        country = domains.get(self.opti_.country)
        default = ''
        if country:
            default = country.default_timezone
        else:
            help_txt.append('')
            help_txt.append(ColorTxt(_('В базе {} нет часового пояса по умолчанию для домена <{}> !!!').format(
                domains.db_file_name, self.opti_.country)).red.bold)

        return self._dialog_menu(items, default, help_txt)

    def dialog_localtime(self) -> Tuple[str, str]:
        items = [('UTC', _('Всемирное координированное время')),
                 ('LOCAL', _('Местное время') + ' ' + ColorTxt(_('(КАТЕГОРИЧЕСКИ НЕ РЕКОМЕНДУЕТСЯ)')).red.bold)]

        help_txt = self._head_txt()
        help_txt += ['', _('Выберите тип аппаратных часов')]

        default = 'UTC'

        return self._dialog_menu(items, default, help_txt)

    def dialog_locale(self) -> Tuple[str, str]:
        timezones = DbTimezones().read()
        locales = DbLocales().read()

        items = locales.menu_items

        help_txt = self._head_txt()
        help_txt += ['', _('Выберите локаль')]

        timezone = timezones.get(self.opti_.timezone, 'timezone')
        default = ''
        if timezone:
            default = timezone.default_locale
        else:
            help_txt.append('')
            help_txt.append(ColorTxt(_('В базе {} нет локали по умолчанию для часового пояса <{}> !!!').format(
                timezones.db_file_name, self.opti_.timezone)).red.bold)

        return self._dialog_menu(items, default, help_txt)

    def dialog_keymap(self) -> Tuple[str, str]:
        locales = DbLocales().read()
        keymaps = DbKeymaps().read()

        items = keymaps.menu_items

        help_txt = self._head_txt()
        help_txt += ['', _('Выберите раскладку клавиатуры')]

        locale = locales.get(self.opti_.locale, 'locale')
        default = ''
        if locale:
            default = locale.default_keymap
        else:
            help_txt.append('')
            help_txt.append(ColorTxt(_('В базе {} нет раскладки по умолчанию для локали <{}> !!!').format(
                locales.db_file_name, self.opti_.locale)).red.bold)

        return self._dialog_menu(items, default, help_txt)

    def dialog_keymap_toggle(self) -> Tuple[str, str]:
        keymaps = DbKeymaps().read()

        items = keymaps.menu_items
        items.insert(0, (self.DEFAULT_ITEM, self.DEFAULT_ITEM))

        help_txt = self._head_txt()
        help_txt += ['', _('Выберите дополнительную раскладку клавиатуры')]

        default = self.DEFAULT_ITEM

        return self._dialog_menu(items, default, help_txt)

    def dialog_font(self) -> Tuple[str, str]:
        locales = DbLocales().read()
        fonts = DbFonts().read()

        items = fonts.menu_items

        help_txt = self._head_txt()
        help_txt += ['', _('Выберите шрифт')]

        locale = locales.get(self.opti_.locale, 'locale')
        default = ''
        if locale:
            default = locale.default_font
        else:
            help_txt.append('')
            help_txt.append(ColorTxt(_('В базе {} нет шрифта по умолчанию для локали <{}> !!!').format(
                locales.db_file_name, self.opti_.locale)).red.bold)

        return self._dialog_menu(items, default, help_txt)

    def dialog_font_map(self) -> Tuple[str, str]:
        fonts = DbFonts().read()
        fontmaps = DbFontMaps().read()

        items = fontmaps.menu_items
        items.insert(0, (self.DEFAULT_ITEM, self.DEFAULT_ITEM))

        help_txt = self._head_txt()
        help_txt += ['', _('Выберите карту шрифта')]

        font = fonts.get(self.opti_.font)
        default = ''
        if font:
            default = font.font_map
        else:
            help_txt.append('')
            help_txt.append(ColorTxt(_('В базе {} нет карты шрифта по умолчанию для шрифта <{}> !!!').format(
                fonts.db_file_name, self.opti_.font)).red.bold)
        if not default:
            default = self.DEFAULT_ITEM

        return self._dialog_menu(items, default, help_txt)

    def dialog_font_unimap(self) -> Tuple[str, str]:
        fonts = DbFonts().read()
        fontunimaps = DbFontUnimaps().read()

        items = fontunimaps.menu_items
        items.insert(0, (self.DEFAULT_ITEM, self.DEFAULT_ITEM))

        help_txt = self._head_txt()
        help_txt += ['', _('Выберите unicode карту шрифта')]

        font = fonts.get(self.opti_.font)
        default = ''
        if font:
            default = font.font_unimap
        else:
            help_txt.append('')
            help_txt.append(ColorTxt(_('В базе {} нет unicode карты шрифта по умолчанию для шрифта <{}> !!!').format(
                fonts.db_file_name, self.opti_.font)).red.bold)
        if not default:
            default = self.DEFAULT_ITEM

        return self._dialog_menu(items, default, help_txt)

    def dialog_mirrorlist(self) -> Tuple[str, List[str]]:
        mirrorlist = MirrorList(self.opti_.country).read_raw()
        choices: List[Tuple[str, str, str]] = sorted(mirrorlist.choices, key=lambda x: (x[1], x[0]))
        default: Tuple[str, ...] = tuple(mirrorlist.default_items)

        help_txt = self._head_txt()
        help_txt += ['', _('Выберите зеркала (от 1 до 6 шт.)')]

        return self._dialog_checklist(choices, default, help_txt)

    def dialog_hostname(self) -> Tuple[str, str]:
        demo_text = 'hostname.domain.org'
        demo_text = ColorTxt(demo_text).blue.bold

        help_txt = self._head_txt()
        help_txt += ['', _('Введите имя компьютера'),
                     demo_text]

        default = 'hostname.' + self.opti_.country.lower()

        return self._dialog_inputbox(default, help_txt)

    # @ModuleInterface.decor_can_not_perform
    def run(self) -> bool:
        self.opti_ = Options()

        code, value = self.dialog_country()
        if code in self.my_dialog.ESC_CANCEL:
            return False
        self.opti_.country = value or self.opti_.__class__.country

        # code, value = self.dialog_timezone()
        # if code in self.my_dialog.ESC_CANCEL:
        #     return False
        # self.opti_.timezone = value or self.opti_.__class__.timezone
        #
        # code, value = self.dialog_localtime()
        # if code in self.my_dialog.ESC_CANCEL:
        #     return False
        # self.opti_.localtime = value or self.opti_.__class__.localtime
        #
        # code, value = self.dialog_locale()
        # if code in self.my_dialog.ESC_CANCEL:
        #     return False
        # self.opti_.locale = value or self.opti_.__class__.locale
        #
        # code, value = self.dialog_keymap()
        # if code in self.my_dialog.ESC_CANCEL:
        #     return False
        # self.opti_.keymap = value or self.opti_.__class__.keymap
        #
        # code, value = self.dialog_keymap_toggle()
        # if code in self.my_dialog.ESC_CANCEL:
        #     return False
        # if value == self.DEFAULT_ITEM:
        #     value = None
        # self.opti_.keymap_toggle = value or self.opti_.__class__.keymap_toggle
        #
        # code, value = self.dialog_font()
        # if code in self.my_dialog.ESC_CANCEL:
        #     return False
        # self.opti_.font = value or self.opti_.__class__.font
        #
        # code, value = self.dialog_font_map()
        # if code in self.my_dialog.ESC_CANCEL:
        #     return False
        # if value == self.DEFAULT_ITEM:
        #     value = None
        # self.opti_.font_map = value or self.opti_.__class__.font_map
        #
        # code, value = self.dialog_font_unimap()
        # if code in self.my_dialog.ESC_CANCEL:
        #     return False
        # if value == self.DEFAULT_ITEM:
        #     value = None
        # self.opti_.font_unimap = value or self.opti_.__class__.font_unimap
        #
        # code, value = self.dialog_hostname()
        # if code in self.my_dialog.ESC_CANCEL:
        #     return False
        # self.opti_.hostname = value or self.opti_.__class__.hostname

        code, value = self.dialog_mirrorlist()
        if code in self.my_dialog.ESC_CANCEL:
            return False
        self.opti_.mirrorlist = value or self.opti_.__class__.mirrorlist

        code = self.dialog_test()
        if code == self.my_dialog.OK:
            return True
