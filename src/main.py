#!/usr/bin/env python3
import gettext
import logging
import os
from gettext import gettext as _

import modules.main
from aai_framework.interface import ModuleInterface
from libs.log import logging_init, DebugFileProxy
from modules.m_main import Module as ModuleMain

logger = logging.getLogger(__name__)

# @todo: Добавить в меню кнопки с поведением esc, что бы была кнопка!!!

PROG_FNAME = os.path.basename(__file__)
RUN_PATH = os.path.abspath(os.path.dirname(__file__))

MODULE_NAME = 'aai2'

GETTEXT_PATH = 'locale'

LOG_FILE = MODULE_NAME + '-install.log'

gettext.bindtextdomain(MODULE_NAME, os.path.abspath(os.path.join(RUN_PATH, GETTEXT_PATH)))
gettext.textdomain(MODULE_NAME)


def arg_parse():
    import argparse

    parser = argparse.ArgumentParser(epilog=modules.main.vars_.config.prog_name,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     allow_abbrev=False)

    default_txt = _('по умолчанию: {}').format('%(default)s')
    parser.add_argument('-p', dest='new_sys_path', type=str, default=modules.main.vars_.cmd_arg.new_sys_path,
                        metavar='tmp_path', nargs=argparse.OPTIONAL,
                        help=_('путь к временной папке, в которую будут примонтированы разделы ({})').format(
                            default_txt))

    parser.add_argument('-g', dest='gdialog', action='store_true',
                        help=_('включение графического режима ({})').format(default_txt))

    parser.add_argument('-d', dest='debug', action='store_true',
                        help=_('режим без проверок выполненных пунктов ({})').format(default_txt))

    parser.add_argument('-m', dest='mini', action='store_true',
                        help=_('режим без проверок выполненных пунктов ({})').format(default_txt))

    # noinspection PyProtectedMember
    parser.add_argument('--loglevel', choices=tuple(logging._nameToLevel),
                        default=modules.main.Args.loglevel,
                        help=_('уровень логирования ({})').format(default_txt))

    parser.add_argument('--version', action='version', version=modules.main.vars_.config.version,
                        help=_('показать номер версии программы и выйти'))

    modules.main.vars_.cmd_arg = parser.parse_args(namespace=modules.main.vars_.cmd_arg)

    logging_init(modules.main.vars_.cmd_arg.loglevel, os.path.join(RUN_PATH, LOG_FILE))

    del argparse


def main():
    arg_parse()

    ModuleInterface.my_dialog.set_background_title(modules.main.vars_.config.prog_name)

    if logging.root.level == logging.DEBUG:
        ModuleInterface.my_dialog.setup_debug(True, DebugFileProxy(), True, expand_file_opt=True)

    module_main = ModuleMain()
    try:
        module_main.run()
    except Exception as e:
        logger.exception(e)
        module_main.run_exit(yes=True)
        raise


if __name__ == '__main__':
    main()
