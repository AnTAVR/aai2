import os
from typing import Tuple, Set, Iterable, List


class MirrorList:
    FILE = 'etc/pacman.d/mirrorlist'
    FILE_RAW = FILE + '.orig'
    DEFAULT_MIRRORS = ('mirrors.kernel.org', 'ftp.fau.de')

    mirrors_raw: Set[str] = None
    _mirrors_save: Set[str] = None
    _country: str = None
    root: str = None

    def __init__(self, country: str = '', root: str = '/'):
        self._country = country.lower()
        self.mirrors_raw = set()
        self._mirrors_save = set()
        self.root = root

    def _get_mirror_str_from_url(self, url: str) -> Iterable[str]:
        return (mirror for mirror in self.mirrors_raw if mirror.find(url) > -1)

    @property
    def mirrors_save(self) -> List[str]:
        ret = set()
        for mirror in self._mirrors_save:
            for mir in self._get_mirror_str_from_url(mirror):
                ret.add(mir)
        return list(ret)

    @mirrors_save.setter
    def mirrors_save(self, val: Iterable[str]):
        self._mirrors_save = set(val)

    @staticmethod
    def _get_url_from_mirror_str(mirror: str) -> str:
        mirror = mirror.split('/', 3)
        mirror = mirror[0:3]
        mirror = '/'.join(mirror)
        return mirror[9:]

    @property
    def mirrors(self) -> List[str]:
        return [self._get_url_from_mirror_str(x) for x in self.mirrors_raw]

    @property
    def choices(self) -> List[Tuple[str, str, str]]:
        """
        :return: {tag}, {item}, {status}
        """
        ret = []
        for tag in self.mirrors:
            item = '-'
            status = 'off'
            index = tag.rfind('.')
            if index > -1:
                item = tag[index + 1:]
                item = item.lower()
                if item == self._country:
                    status = 'on'
            ret.append((tag, item, status))
        return ret

    @classmethod
    def _find_default(cls, tag: str) -> bool:
        for default in cls.DEFAULT_MIRRORS:
            if tag.find(default) > -1:
                return True
        return False

    @property
    def default_items(self) -> List[str]:
        return [tag for tag, item, status in self.choices if self._find_default(tag)]

    def _read_file(self, path: str, root: str = None):
        if root is None:
            root = self.root

        with open(os.path.join(root, path)) as f:
            for line in f:
                line = line.strip()
                if line.startswith('Server = '):
                    pass
                elif line.startswith('#Server = '):
                    line = line[1:]
                else:
                    continue
                yield line

    def read_raw(self, root: str = None):
        self.mirrors_raw = set(self._read_file(self.FILE_RAW, root))
        return self

    def read_save(self, root: str = None):
        self._mirrors_save = set(self._get_url_from_mirror_str(line) for line in self._read_file(self.FILE, root))
        return self

    def write_save(self, root: str = None):
        if root is None:
            root = self.root
        with open(os.path.join(root, self.FILE), 'w') as f:
            f.writelines(self.mirrors_save)

        return self
