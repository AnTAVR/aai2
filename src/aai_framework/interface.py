import collections
import functools
from abc import ABCMeta, abstractmethod
from gettext import gettext as _
from typing import TypeVar, Union, Optional, List, Tuple, Callable, Any, Iterable

from .dial import MyDialog, ColorTxt
from .utils import VarsRepr

_ModuleInterfaceType = TypeVar('_ModuleInterfaceType', bound='ModuleInterface')


class _Collection(collections.Collection):
    def __init__(self, *args: _ModuleInterfaceType):
        self._list = []  # type: List[_ModuleInterfaceType]
        self.add(*args)

    def __contains__(self, key: str) -> bool:
        return key in self._list

    def __iter__(self) -> Iterable[_ModuleInterfaceType]:
        return iter(self._list)

    def __len__(self):
        return len(self._list)

    def __repr__(self) -> str:
        return repr(self._list)

    def __getitem__(self, item: Union[str, int]) -> _ModuleInterfaceType:
        for i, x in enumerate(self._list):  # type: int, _ModuleInterfaceType
            if item in (x.ID, i):
                return x
        raise IndexError

    def clear(self):
        self._list.clear()

    def add(self, *args):
        for x in args:
            if x not in self._list:
                self._list.append(x)


class RelationCollection(_Collection):
    def __init__(self, *args: _ModuleInterfaceType, attr: str):
        self.__attr = attr
        super().__init__(*args)

    @property
    def txt(self) -> Optional[List[str]]:
        ret: List[str] = []
        for _module in self:  # type: ModuleInterface
            txt_ = getattr(_module, self.__attr)
            if txt_ is not None:
                ret.append(txt_)

        if ret:
            return ret


class ModuleCollection(_Collection):
    @property
    def menu_items(self) -> List[Tuple[str, str]]:
        return [mod.menu_item for mod in self]


class ModuleInterface(metaclass=ABCMeta):
    ID: str = None
    LEN_INSTALL: int = None

    conflicts: RelationCollection = None
    depends: RelationCollection = None

    is_run: bool = False

    my_dialog = MyDialog()

    def __init__(self):
        assert self.ID is not None

        self.conflicts = RelationCollection(attr='is_run_txt')
        self.depends = RelationCollection(attr='is_not_run_txt')

    @property
    @abstractmethod
    def name(self) -> str:
        return ''

    @property
    @abstractmethod
    def vars_(self) -> VarsRepr:
        return VarsRepr()

    def get_menu_item(self, text_new: Optional[List[str]] = None) -> Tuple[str, str]:
        text = [self.name]
        if self.LEN_INSTALL is not None:
            text.append(ColorTxt('({}MiB)'.format(self.LEN_INSTALL)).cyan)
        # noinspection PyUnresolvedReferences
        if ModuleInterface.run.__code__ == self.run.__code__:
            text.append(ColorTxt('(' + _('Пока не поддерживается') + ')').red.bold)
        elif text_new is not None:
            text.extend(x for x in text_new if x is not None)
        return self.ID, ' '.join(text)

    @property
    def menu_item(self) -> Tuple[str, str]:
        return self.get_menu_item()

    def dialog_not_supported(self) -> str:
        help_txt: List[str] = [ColorTxt('(' + _('Пока не поддерживается') + ')').red.bold,
                               _('Помогите проекту, допишите данный функционал.')]

        text = '\n'.join(help_txt)  # type: str

        return self._dialog_msgbox(text)

    # @abstractmethod
    # noinspection PyUnusedLocal
    def run(self, *args, **kwargs):
        self.dialog_not_supported()

    @property
    def is_run_txt(self) -> Optional[str]:
        if self.is_run:
            return ColorTxt(_('Пункт <{}> уже выполнен.')).red.bold.format(self.name)

    @property
    def is_not_run_txt(self) -> Optional[str]:
        if not self.is_run:
            return ColorTxt(_('Пункт <{}> не выполнен.')).red.bold.format(self.name)

    def dialog_can_not_perform(self, help_txt: Optional[List[str]]) -> Optional[str]:
        if help_txt is None:
            return
        help_txt.append('')
        help_txt.append(ColorTxt(_('Выполнение невозможно.')).red.bold)
        text = '\n'.join(help_txt)

        return self._dialog_msgbox(text)

    @staticmethod
    def decor_can_not_perform(func: Callable[[_ModuleInterfaceType, Any], Any]):
        @functools.wraps(func)
        def wrapper(self: ModuleInterface, *args, **kwargs):
            if self.dialog_can_not_perform(self.conflicts.txt) is not None or \
                    self.dialog_can_not_perform(self.depends.txt) is not None:
                return
            return func(self, *args, **kwargs)

        return wrapper

    def _dialog_menu(self, choices: Iterable[Tuple[str, str]], default: str = '', help_txt: List[str] = None,
                     **kwargs) -> Tuple[str, str]:
        if help_txt is None:
            txt_ = _('Выберите действие')  # type: str
            help_txt = [txt_]

        if default:
            help_txt.append('')
            help_txt.append(_('по умолчанию: {}').format(ColorTxt(default).bold))

        text = '\n'.join(help_txt)

        return self.my_dialog.menu(text, title=self.name, choices=choices, default_item=default, **kwargs)

    @staticmethod
    def _checklist_color(val: Tuple[str, str, str], default: Iterable[str]) -> Tuple[str, str, str]:
        tag, item, status = val
        if tag in default:
            item = ColorTxt(item).green.bold
            return tag, item, status
        return val

    def _dialog_checklist(self, choices: Iterable[Tuple[str, str, str]], default: Iterable[str] = None,
                          help_txt: List[str] = None, **kwargs) -> Tuple[str, List[str]]:
        if default is None:
            default = tuple()

        if help_txt is None:
            txt_ = _('Выберите опции')  # type: str
            help_txt = [txt_]

        help_txt.append('')
        help_txt.append(_('по умолчанию: {}').format(ColorTxt(_('выделено')).green.bold))

        choices_ = map(lambda x: self._checklist_color(x, default), choices)

        text = '\n'.join(help_txt)

        return self.my_dialog.checklist(text, title=self.name, choices=choices_, **kwargs)

    def _dialog_inputbox(self, default: str = '', help_txt: List[str] = None, **kwargs) -> Tuple[str, str]:
        if help_txt is None:
            help_txt = []

        if default:
            help_txt.append('')
            help_txt.append(_('по умолчанию: {}').format(ColorTxt(default).bold))

        text = '\n'.join(help_txt)

        return self.my_dialog.inputbox(text, title=self.name, init=default, **kwargs)

    def _dialog_msgbox(self, text: str, **kwargs) -> str:
        return self.my_dialog.msgbox(text, title=self.name, **kwargs)

    def _dialog_err(self, text: str, **kwargs) -> str:
        text = ColorTxt(text).red.bold
        return self.my_dialog.msgbox(text, title=self.name, **kwargs)


class DialogTestInterface(metaclass=ABCMeta):
    name: str
    my_dialog: MyDialog

    # noinspection PyUnusedLocal
    @abstractmethod
    def _head_txt(self, help_txt_new: List[str] = None, all_: bool = False) -> List[str]:
        return ['']

    @classmethod
    def color_head_txt(cls, text: str, key: str, val: Optional[str]) -> str:
        if val is None:
            ret = text.format(key, ColorTxt(val).yellow.bold)
        else:
            ret = text.format(key, ColorTxt(val).green.bold)
        return ret

    @staticmethod
    def format_head_txt(help_list: List[Tuple[str, str, str, bool]]) -> List[str]:
        help_txt = []
        for help_str, value_name, value, print_is_none in help_list:
            # if value is not None or print_is_none:
            if value or print_is_none:
                help_txt.append(DialogTestInterface.color_head_txt(help_str, value_name, value))

        return help_txt

    def dialog_test(self) -> str:
        help_txt: List[str] = [_('Подтвердите свой выбор'), ''] + self._head_txt(all_=True)
        help_txt: str = '\n'.join(help_txt)

        return self.my_dialog.yesno(help_txt, title=self.name, defaultno=True)
