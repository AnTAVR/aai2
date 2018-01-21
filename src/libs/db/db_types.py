import logging
from gettext import gettext as _
from typing import Tuple

from .db_lib import NamedList
from .db_lib1 import list_consoletrans, list_unimaps, list_consolefonts, list_kbd_model_maps, list_kbd_keymaps, \
    list_zones, \
    list_iso3166s, list_locale_gens

logger = logging.getLogger(__name__)


class FontMapsList(NamedList):
    keys = ('font_map',)

    font_map: str

    @classmethod
    def get_new(cls, scan_path=''):
        lines = list_consoletrans(scan_path)

        lines = map(lambda x: cls(x), lines)
        return list(lines)

    @property
    def menu_item(self) -> Tuple[str, str]:
        return self.font_map, '-'


class FontUnimapsList(NamedList):
    keys = ('font_unimap',)

    font_unimap: str

    @classmethod
    def get_new(cls, scan_path=''):
        lines = list_unimaps(scan_path)

        lines = map(lambda x: cls(x), lines)
        return list(lines)

    @property
    def menu_item(self) -> Tuple[str, str]:
        return self.font_unimap, '-'


class FontsList(NamedList):
    keys = ('unicode', 'font', 'font_map', 'font_unimap')

    font: str
    unicode: str
    font_map: str
    font_unimap: str

    @classmethod
    def get_new(cls, scan_path=''):
        lines = list_consolefonts(scan_path)

        lines = map(lambda x: cls(x), lines)
        return list(lines)

    @property
    def menu_item(self) -> Tuple[str, str]:
        return self.font, self.unicode


class KeymapsList(NamedList):
    keys = ('architecture', 'keymap', 'xlayout', 'xmodel', 'xvariant', 'xoptions')

    keymap: str
    architecture: str
    xlayout: str
    xmodel: str
    xvariant: str
    xoptions: str

    @classmethod
    def get_new(cls, scan_path=''):
        def correct(x):
            xlayout: list = x[1].split(',')
            xoptions: list = x[4].split(',')

            try:
                xlayout.remove('us')
            except ValueError:
                pass
            else:
                x[1] = ','.join(['us'] + xlayout)

            try:
                index = xoptions.index('grp:shifts_toggle')
            except ValueError:
                pass
            else:
                xoptions[index] = 'grp:alt_shift_toggle'
                x[4] = ','.join(xoptions)

            return x

        lines = []

        _kbdmodelmaps = list_kbd_model_maps(scan_path)
        _kbdmodelmaps = list(map(correct, _kbdmodelmaps))

        for keymaps in list_kbd_keymaps(scan_path):
            kbdmodelmaps = [x for x in _kbdmodelmaps if x[0] == keymaps[1]]
            if kbdmodelmaps:
                kbdmodelmap = kbdmodelmaps[0][1:]
            else:
                kbdmodelmap = [''] * 4
            lines.append(keymaps + kbdmodelmap)

        lines = map(lambda x: cls(x), lines)
        return list(lines)

    @property
    def menu_item(self) -> Tuple[str, str]:
        return self.keymap, self.architecture


class DomainsList(NamedList):
    keys = ('domain', 'country', 'default_timezone')

    domain: str
    country: str
    default_timezone: str

    @classmethod
    def get_new(cls, scan_path=''):
        # noinspection PyPep8Naming
        COUNTRYS_MULTI_TZ = {
            'AQ': 'Antarctica/Vostok',
            'AU': 'Australia/Brisbane',
            'BR': 'America/Belem',
            'CA': 'America/Goose_Bay',
            'CL': 'America/Santiago',
            'CY': 'Asia/Nicosia',
            'ES': 'Europe/Madrid',
            'FM': 'Pacific/Pohnpei',
            'GL': 'America/Godthab',
            'KI': 'Pacific/Tarawa',
            'MH': 'Pacific/Majuro',
            'MN': 'Asia/Ulaanbaatar',
            'MX': 'America/Mexico_City',
            'PF': 'Pacific/Marquesas',
            'PG': 'Pacific/Port_Moresby',
            'PT': 'Europe/Lisbon',
            'RU': 'Europe/Moscow',
            'US': 'America/Los_Angeles',
            'UZ': 'Asia/Tashkent',
            'AR': 'America/Argentina/Buenos_Aires',
            'CD': 'Africa/Kinshasa',
            'CN': 'Asia/Shanghai',
            'DE': 'Europe/Berlin',
            'EC': 'America/Guayaquil',
            'ID': 'Asia/Jakarta',
            'KZ': 'Asia/Almaty',
            'MY': 'Asia/Kuala_Lumpur',
            'NZ': 'Pacific/Auckland',
            'PS': 'Asia/Gaza',
            'UA': 'Europe/Kiev',
            'UM': 'Pacific/Midway',
        }

        lines = []

        _zones = list_zones(scan_path)

        for countrys in list_iso3166s(scan_path):
            country = countrys[0]
            zones = [x[2] for x in _zones if x[0] == country]
            zone = ''
            if zones:
                zone = zones[0]
                if len(zones) > 1:
                    try:
                        zone_old = COUNTRYS_MULTI_TZ[country]
                        if not [x for x in zones if x == zone_old]:
                            logger.error(_('"{}" TZ "{}" not correct, set "{}"').format(country, zone_old, zone))
                        else:
                            zone = zone_old
                    except KeyError:
                        logger.warning(_('"{}" multi TZ , set "{}"').format(country, zone))

            lines.append(countrys + [zone])

        lines = map(lambda x: cls(x), lines)
        return list(lines)

    @property
    def menu_item(self) -> Tuple[str, str]:
        return self.domain, self.country


class TimezonesList(NamedList):
    keys = ('domain', 'timezone', 'default_locale', 'coordinates', 'comment')

    timezone: str
    domain: str
    default_locale: str
    coordinates: str
    comment: str

    @classmethod
    def get_new(cls, scan_path=''):
        # noinspection PyPep8Naming
        CHARSET_PRIORITY = ('UTF-8', 'ISO-8859-1')
        # noinspection PyPep8Naming
        LANGUAGE_PRIORITY = (('Asia/Nicosia', 'tr'),
                             ('Asia/Famagusta', 'el'),
                             ('Asia/Urumqi', 'ug'),
                             ('Africa/Addis_Ababa', 'am'),
                             ('Africa/Nairobi', 'sw'),
                             ('Europe/Luxembourg', 'lb'),
                             ('Asia/Karachi', 'ur'),
                             'ru', 'en', 'zh',)

        lines = []

        _locales = list_locale_gens(scan_path)
        _locales = sorted(_locales, key=lambda x: x[2].upper())

        def charset_priority(loc):
            for charset in CHARSET_PRIORITY:
                charset_locales = tuple(filter(lambda x: x[3] == charset, loc))
                if charset_locales:
                    ret = language_priority(charset_locales)
                    if ret:
                        return ret

        def language_priority(loc):
            language_locales = tuple(filter(lambda x: x[1] == x[2].lower(), loc))
            if language_locales:
                ret = language_locales[0][0]
                if ret:
                    return ret

            for language in LANGUAGE_PRIORITY:
                if isinstance(language, tuple) and language[0] == zone[2]:
                    language = language[1]
                language_locales = tuple(filter(lambda x: x[1] == language, loc))
                if language_locales:
                    ret = language_locales[0][0]
                    if ret:
                        return ret

            return loc[0][0]

        for zone in list_zones(scan_path):
            country = zone[0]
            locales = list(filter(lambda x: x[2] == country, _locales))
            locale = ''
            if locales:
                locale = locales[0][0]
                if len(locales) > 1:
                    locale_ = charset_priority(locales)
                    if locale_:
                        locale = locale_
            value = [zone[0], zone[2]] + [locale] + [zone[1]] + zone[3:]
            lines.append(value)

        lines = map(lambda x: cls(x), lines)
        return list(lines)

    @property
    def menu_item(self) -> Tuple[str, str]:
        return self.timezone, self.domain + ' ' + self.comment


class LocalesList(NamedList):
    keys = ('domain', 'locale', 'default_keymap', 'default_font')

    locale: str
    domain: str
    default_keymap: str
    default_font: str

    @classmethod
    def get_new(cls, scan_path=''):
        # noinspection PyPep8Naming
        KEYMAPS_PRIORITY = {
            'BG': 'bg-cp1251',
            'BR': 'pt-latin1',
            'IS': 'is-latin1',
            'PT': 'pt-latin1',
            'SK': 'sk-qwerty',
        }

        # noinspection PyPep8Naming
        FILTERS = [
            lambda x: x[1].lower() == locale[5].lower(),
            lambda x: x[1].lower() == locale[0].lower(),
            lambda x: x[1].lower().startswith(locale[5].lower() + '-'),
            lambda x: x[1].lower().startswith(locale[0].lower() + '-'),
        ]

        lines = []

        _locales = list_locale_gens(scan_path)
        _locales = sorted(_locales, key=lambda x: x[2].upper())

        _keymaps = list_kbd_keymaps(scan_path)

        for countrys in list_iso3166s(scan_path):
            country = countrys[0]
            locales = [x for x in _locales if x[2] == country]
            if locales:
                lines += list(map(lambda x: [x[2], x[0], '', '', x[3], x[1]], locales))
            else:
                lines += [[country] + [''] * 5]

        lines = list(map(lambda x: x if x[5] != 'en' else x[:5] + ['us'], lines))

        for locale in lines:
            for d in FILTERS:
                keymaps_locale = tuple(filter(d, _keymaps))
                if keymaps_locale:
                    if len(keymaps_locale) > 1:
                        try:
                            keymap = KEYMAPS_PRIORITY[locale[1]]
                        except KeyError:
                            try:
                                keymap = KEYMAPS_PRIORITY[locale[0]]
                            except KeyError:
                                keymap = keymaps_locale[0][1]
                                logger.warning(_('"{}" multi keymap, set "{}"').format(locale[1], keymap))
                        locale[2] = keymap
                    else:
                        locale[2] = keymaps_locale[0][1]
                    break

        lines = map(lambda x: cls(x), lines)
        return list(lines)

    @property
    def menu_item(self) -> Tuple[str, str]:
        return self.locale, self.domain
