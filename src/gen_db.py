#!/usr/bin/env python3
import logging
import os
from gettext import gettext as _

from libs.db import DbFontMaps, DbFontUnimaps, DbFonts, DbKeymaps, DbDomains, DbTimezones, DbLocales

logger = logging.getLogger(__name__)

__version__ = '0.1'

RUN_PATH = os.path.abspath(os.path.dirname(__file__))


def arg_parse():
    import argparse
    parser = argparse.ArgumentParser()

    default_txt = _('по умолчанию: "{}"').format('%(default)s')
    # noinspection PyProtectedMember
    parser.add_argument('--loglevel', choices=tuple(logging._nameToLevel),
                        default=logging.getLevelName(logging.DEBUG),
                        help=_('уровень логирования ({})').format(default_txt))

    params = parser.parse_args()

    logging.root.setLevel(params.loglevel)
    del argparse


def main():
    arg_parse()

    DbFontMaps(save_path=RUN_PATH).generate().write(True)
    DbFontUnimaps(save_path=RUN_PATH).generate().write(True)
    DbFonts(save_path=RUN_PATH).generate().write(True)
    DbKeymaps(save_path=RUN_PATH).generate().write(True)
    DbDomains(save_path=RUN_PATH).generate().write(True)
    DbTimezones(save_path=RUN_PATH).generate().write(True)
    DbLocales(save_path=RUN_PATH).generate().write(True)


if __name__ == '__main__':
    main()
