import logging
from gettext import gettext as _
from typing import Tuple, Generator, List

from libs.part import get_mem, size_convert
from vendor.partinfo.all import Device

logger = logging.getLogger(__name__)


def get_min_max_swap_size(val):
    _size = round(val + .49)

    min_size = _size + 1

    max_size = _size * 2
    if _size > 7:
        max_size = min_size

    rek = (max_size + min_size) / 2
    return min_size, max_size, round(rek + .49)


def default_size_swap() -> Tuple[int, int, str]:
    mem_size = get_mem()
    mem_size_gib = size_convert.size_to(mem_size, 'g')

    unit = mem_size_gib[1]
    mem_size_gib = mem_size_gib[0]

    r = get_min_max_swap_size(mem_size_gib)

    return round(r[0]), round(r[1]), unit


SWAP_FS_TYPES = ('ext2', 'ext3', 'ext4')
NONE_ITEM_ID = 'None'


def format_items(devs: Generator[Device, None, None]) -> List[Tuple[str, str]]:
    items: List[Tuple[str, str]] = [(dev.devname, ' '.join(
        map(lambda x: str(x), filter(lambda x: x, (
            dev.boot,
            dev.id_bus,
            dev.id_part_table_type,
            dev.id_fs_type,
            '{:.1f}{}'.format(*size_convert.natural_size(dev.size)),
            dev.model_dec,
        )))))
                                    for dev in devs
                                    ]
    if not items:
        items: List[Tuple[str, str]] = [(NONE_ITEM_ID, _('Подходящие накопители не найдены!!!'))]
    return items
