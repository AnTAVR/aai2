import logging

from aai_framework.utils import VarsRepr

logger = logging.getLogger(__name__)


class Vars(VarsRepr):
    @property
    def _repr__props(self) -> list:
        return []

    @property
    def is_ok(self) -> bool:
        return False


vars_ = Vars()
