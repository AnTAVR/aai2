import csv
import fnmatch
import logging
import os
import re
from abc import ABCMeta, abstractclassmethod
from gettext import gettext as _
from typing import Any, Union, Iterator, List, Tuple, Optional, Generator, Type

logger = logging.getLogger(__name__)

COMMENT_PATTERN = re.compile(r'^#')


def set_len_list(x: Union[list, tuple, any], new_len: int, new_value: Any = None) -> list:
    """Увеличивает или уменьшает размер списка."""
    if isinstance(x, tuple):
        x = list(x)
    elif not isinstance(x, list):
        x = [x]

    lens = new_len - len(x)

    if lens < 0:
        x = x[: new_len]
    elif lens > 0:
        x = x + [new_value] * lens

    return x


def get_files(directorys: Union[str, Iterator], mask: Union[str, tuple, None] = None):
    """Генератор рекурсивно обходит папку и возвращает имя файла (с относительным путем) и расширение.

    :return [dir+file_name, ext]
    """
    if mask is None:
        mask = '*'
    if isinstance(mask, str):
        mask = (mask,)

    if isinstance(directorys, str):
        directorys = (directorys,)

    mask_pattern = re.compile(r'|'.join(map(fnmatch.translate, mask)))

    for directory in directorys:
        if directory[-1] != os.path.sep:
            directory += os.path.sep

        len_directory = len(directory)
        for dir_path, dir_names, file_names in os.walk(directory):
            for file_name in file_names:
                file_name = os.path.join(dir_path, file_name)[len_directory:]
                if mask_pattern.match(file_name):
                    yield os.path.splitext(file_name)


class NamedList(list, metaclass=ABCMeta):
    keys: tuple
    default = None

    def __init__(self, seq=()):
        seq = set_len_list(seq, len(self.keys), self.default)
        super().__init__(seq)

    @classmethod
    def get_index(cls, item: str):
        try:
            index = cls.keys.index(item)
        except ValueError as e:
            raise NamedListAttributeError(cls, item) from e
        return index

    def __getattr__(self, item):
        index = self.get_index(item)
        return self[index]

    def __setattr__(self, item, value):
        index = self.get_index(item)
        self[index] = value

    def __repr__(self):
        args = []
        for key in self.keys:
            args.append('{}={!r}'.format(key, self.__getattr__(key)))

        return "{}({})".format(type(self).__name__, ', '.join(args))

    # noinspection PyMethodParameters
    @abstractclassmethod
    def get_new(cls, scan_path=''):
        return [NamedList()]

    @property
    @abstractclassmethod
    def menu_item(self) -> Tuple[str, str]:
        pass


class NamedListAttributeError(AttributeError):
    def __init__(self, object_: Type[NamedList], item_):
        mess = "{!r} object has no attribute {!r} {!r}".format(object_.__name__, item_, object_.keys)
        super().__init__(mess)


class DbInterface:
    lines: List[NamedList]
    scan_path: str
    save_path: str
    NEW_EXT = '.new'
    DB_DIR = 'db'

    db_file_name: str
    row_class: NamedList

    def __init__(self, scan_path='', save_path='.'):
        self.lines = []
        self.scan_path = scan_path
        self.save_path = os.path.abspath(os.path.join(save_path, self.DB_DIR))

    def generate(self):
        self.lines = self.row_class.get_new(self.scan_path)
        return self

    def write(self, new=False):
        db_file_name_new = self.db_file_name
        if new:
            db_file_name_new += self.NEW_EXT

        db_file_name = os.path.join(self.save_path, db_file_name_new)

        with open(db_file_name, 'w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter='\t')  # type: csv.DictWriter
            csv_writer.writerows(self.lines)
        logger.info(_('Writen "{}".').format(db_file_name))
        return self

    def read(self, new=False):
        db_file_name_new = self.db_file_name
        if new:
            db_file_name_new += self.NEW_EXT

        db_file_name = os.path.join(self.save_path, db_file_name_new)
        lines = []
        with open(db_file_name, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')  # type: csv.DictReader
            for row in csv_reader:
                # noinspection PyCallingNonCallable
                lines.append(self.row_class(row))

        self.lines = lines

        logger.info(_('Reade "{}".').format(db_file_name))
        return self

    @property
    def menu_items(self) -> List[Tuple[str, str]]:
        items = [line.menu_item for line in self.lines]
        items = list(filter(lambda x: x[0], items))
        return items

    def get(self, value: str, item: str = None) -> Optional[NamedList]:
        for line in self.get_all(value, item):
            return line

    def get_all(self, value: str, item: str = None) -> Generator[NamedList, Any, None]:
        index = 0
        if item is not None:
            index = self.row_class.get_index(item)

        for line in self.lines:
            if line[index] == value:
                yield line
