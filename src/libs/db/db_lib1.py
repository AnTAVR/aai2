import os
import re

from .db_lib import get_files, set_len_list, COMMENT_PATTERN

KBD_KEYMAP_DIRS = (
    '/usr/share/keymaps/',
    '/usr/share/kbd/keymaps/',
    '/usr/lib/kbd/keymaps/',
    '/lib/kbd/keymaps/',
)


def list_kbd_keymaps(scan_path: str = '') -> list:
    """Возвращает отсортированный список [type, keymap] из /usr/share/kbd/keymaps.

    :return [type, keymap]
    """

    directory = map(lambda x: os.path.join(scan_path, x), KBD_KEYMAP_DIRS)
    mask = ('*.map.gz', '*.map')

    lines = [os.path.splitext(file_name[0]) for file_name in get_files(directory, mask)]

    lines = map(lambda x: x[0].rsplit(os.path.sep, 1), lines)
    lines = map(lambda x: set_len_list(x, 2, ''), lines)

    lines = sorted(lines, key=lambda x: (x[0] + ' ' + x[1]).upper())

    return list(lines)


def list_i18n_charmaps(scan_path: str = '') -> list:
    """Возвращает отсортированный список "charmap" из /usr/share/i18n/charmaps.

    :return [charmap, ...]
    """
    directory = '/usr/share/i18n/charmaps'
    directory = os.path.join(scan_path, directory)
    mask = '*'

    lines = [file_name[0] for file_name in get_files(directory, mask)]

    lines = sorted(lines, key=lambda x: x.upper())

    return list(lines)


def list_i18n_locales(scan_path: str = '') -> list:
    """Возвращает отсортированный список [locale, language, language_name] из /usr/share/i18n/locales.

    :return [language, language_name]
    """
    directory = '/usr/share/i18n/locales'
    directory = os.path.join(scan_path, directory)
    mask = '*'

    lines = []

    locales = [os.path.splitext(file_name[0])[0]
               for file_name in get_files(directory, mask)
               if file_name[0] not in ('POSIX', 'i18n')
               and not file_name[0].startswith(('translit_', 'iso14651'))]

    locales = sorted(locales, key=lambda x: x.upper())

    for locale in locales:
        file_name = directory + os.path.sep + locale
        with open(file_name, 'r') as f:
            language = map(lambda x: x.strip(), f)
            language = filter(lambda x: x != '', language)

            language = filter(lambda x: x.startswith('language'), language)
            language = map(lambda x: x.split('"')[1].strip(), language)

            lines.append([locale, locale.split('_')[0], list(language)[0]])

    return list(lines)


def list_kbd_model_maps(scan_path: str = '') -> list:
    """Возвращает отсортированный список параметров из /usr/share/systemd/kbd-model-map.

    :return [consolelayout, xlayout, xmodel, xvariant, xoptions]
    """
    file_name = '/usr/share/systemd/kbd-model-map'
    file_name = os.path.join(scan_path, file_name)

    # noinspection PyPep8Naming
    KBD_MODEL_MAP_PATTERN = re.compile(r'[ \t]+')

    with open(file_name, 'r') as f:
        lines = map(lambda x: x.strip(), f)
        lines = filter(lambda x: x != '', lines)

        lines = filter(lambda x: not COMMENT_PATTERN.match(x), lines)

        lines = map(lambda x: KBD_MODEL_MAP_PATTERN.sub('\t', x), lines)

        lines = map(lambda x: x.split('\t'), lines)
        lines = map(lambda x: set_len_list(x, 5, ''), lines)

        lines = sorted(lines, key=lambda x: x[0].upper())

        lines = list(lines)

    return lines


def list_iso3166s(scan_path: str = '') -> list:
    """Возвращает отсортированный список [country, country_name] из /usr/share/zoneinfo/iso3166.tab.

    :return [country, country_name]
    """
    file_name = '/usr/share/zoneinfo/iso3166.tab'
    file_name = os.path.join(scan_path, file_name)

    with open(file_name, 'r') as f:
        lines = map(lambda x: x.strip(), f)
        lines = filter(lambda x: x != '', lines)

        lines = filter(lambda x: not COMMENT_PATTERN.match(x), lines)

        lines = map(lambda x: x.split('\t'), lines)
        lines = map(lambda x: set_len_list(x, 2, ''), lines)

        lines = sorted(lines, key=lambda x: x[0].upper())

        lines = list(lines)

    return lines


def list_zones(scan_path: str = '') -> list:
    """Возвращает отсортированный список [country, coordinates, TZ, comments] из /usr/share/zoneinfo/zone.tab.

    :return [country, coordinates, TZ, comments]
    """
    file_name = '/usr/share/zoneinfo/zone.tab'
    file_name = os.path.join(scan_path, file_name)

    with open(file_name, 'r') as f:
        lines = map(lambda x: x.strip(), f)
        lines = filter(lambda x: x != '', lines)

        lines = filter(lambda x: not COMMENT_PATTERN.match(x), lines)

        lines = map(lambda x: x.split('\t'), lines)
        lines = map(lambda x: set_len_list(x, 4, ''), lines)

        lines = sorted(lines, key=lambda x: (x[0] + ' ' + x[2]).upper())

        lines = list(lines)

    return lines


def list_locale_gens(scan_path: str = '') -> list:
    """Возвращает отсортированный список [locale, language, country, charset] из /etc/locale.gen.

    :return [locale, language, country, charset]
    """
    file_name = '/etc/locale.gen'
    file_name = os.path.join(scan_path, file_name)

    # noinspection PyPep8Naming
    LOCALE_GEN_PATTERN = re.compile(r'^#[a-z]')

    with open(file_name, 'r') as f:
        locales = map(lambda x: x.strip(), f)
        locales = filter(lambda x: x != '', locales)

        locales = filter(lambda x: LOCALE_GEN_PATTERN.match(x), locales)
        locales = map(lambda x: x.strip('#'), locales)

        locales = map(lambda x: x.split(' '), locales)
        locales = map(lambda x: set_len_list(x, 2, ''), locales)

        locales = sorted(locales, key=lambda x: (x[0] + ' ' + x[1]).upper())

        lines = []
        for locale in locales:
            country = locale[0].split('.')
            country = country[0].split('@')
            country = country[0].split('_')
            country = set_len_list(country, 2, '')
            lines.append([' '.join(locale)] + country + [locale[1]])

    return lines


def list_consoletrans(scan_path=''):
    """Возвращает отсортированный список "consoletrans" из /usr/share/kbd/consoletrans.

    :return [consoletrans, ...]
    """
    directory = '/usr/share/kbd/consoletrans'
    directory = os.path.join(scan_path, directory)
    mask = '*.trans'

    lines = [file_name[0] for file_name in get_files(directory, mask)]

    lines = sorted(lines, key=lambda x: x.upper())

    return list(lines)


def list_unimaps(scan_path=''):
    """Возвращает отсортированный список "unimap" из /usr/share/kbd/unimaps.

    :return [unimap, ...]
    """
    directory = '/usr/share/kbd/unimaps'
    directory = os.path.join(scan_path, directory)
    mask = '*.uni'

    lines = [file_name[0] for file_name in get_files(directory, mask)]

    lines = sorted(lines, key=lambda x: x.upper())

    return list(lines)


def list_consolefonts(scan_path=''):
    """Возвращает отсортированный список [type, consolefont] из /usr/share/kbd/consolefonts.

    :return [type, consolefont]
    """
    directory = '/usr/share/kbd/consolefonts'
    directory = os.path.join(scan_path, directory)
    mask = ('*.psfu.gz', '*.psf.gz')

    lines = [os.path.splitext(file_name[0]) for file_name in get_files(directory, mask)]

    lines = map(lambda x: [x[1][1:], x[0]], lines)

    lines = sorted(lines, key=lambda x: (x[0] + ' ' + x[1]).upper())

    return list(lines)
