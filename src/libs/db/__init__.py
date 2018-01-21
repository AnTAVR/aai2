from typing import Optional, Generator, Any, List

from .db_lib import DbInterface
from .db_types import FontMapsList, FontUnimapsList, FontsList, KeymapsList, DomainsList, TimezonesList, LocalesList


class DbFontMaps(DbInterface):
    db_file_name = 'font_maps.csv'
    row_class = FontMapsList

    lines: List[FontMapsList]

    def get(self, value: str, item: str = None) -> Optional[FontMapsList]:
        return super().get(value, item)

    def get_all(self, value: str, item: str = None) -> Generator[FontMapsList, Any, None]:
        # noinspection PyTypeChecker
        return super().get_all(value, item)


class DbFontUnimaps(DbInterface):
    db_file_name = 'font_unimaps.csv'
    row_class = FontUnimapsList

    lines: List[FontUnimapsList]

    def get(self, value: str, item: str = None) -> Optional[FontUnimapsList]:
        return super().get(value, item)

    def get_all(self, value: str, item: str = None) -> Generator[FontUnimapsList, Any, None]:
        # noinspection PyTypeChecker
        return super().get_all(value, item)


class DbFonts(DbInterface):
    db_file_name = 'fonts.csv'
    row_class = FontsList

    lines: List[FontsList]

    def get(self, value: str, item: str = None) -> Optional[FontsList]:
        return super().get(value, item)

    def get_all(self, value: str, item: str = None) -> Generator[FontsList, Any, None]:
        # noinspection PyTypeChecker
        return super().get_all(value, item)


class DbKeymaps(DbInterface):
    db_file_name = 'keymaps.csv'
    row_class = KeymapsList

    lines: List[KeymapsList]

    def get(self, value: str, item: str = None) -> Optional[KeymapsList]:
        return super().get(value, item)

    def get_all(self, value: str, item: str = None) -> Generator[KeymapsList, Any, None]:
        # noinspection PyTypeChecker
        return super().get_all(value, item)


class DbDomains(DbInterface):
    db_file_name = 'domains.csv'
    row_class = DomainsList

    lines: List[DomainsList]

    def get(self, value: str, item: str = None) -> Optional[DomainsList]:
        return super().get(value, item)

    def get_all(self, value: str, item: str = None) -> Generator[DomainsList, Any, None]:
        # noinspection PyTypeChecker
        return super().get_all(value, item)


class DbTimezones(DbInterface):
    db_file_name = 'timezones.csv'
    row_class = TimezonesList

    lines: List[TimezonesList]

    def get(self, value: str, item: str = None) -> Optional[TimezonesList]:
        return super().get(value, item)

    def get_all(self, value: str, item: str = None) -> Generator[TimezonesList, Any, None]:
        # noinspection PyTypeChecker
        return super().get_all(value, item)


class DbLocales(DbInterface):
    db_file_name = 'locales.csv'
    row_class = LocalesList

    lines: List[LocalesList]

    def get(self, value: str, item: str = None) -> Optional[LocalesList]:
        return super().get(value, item)

    def get_all(self, value: str, item: str = None) -> Generator[LocalesList, Any, None]:
        # noinspection PyTypeChecker
        return super().get_all(value, item)
