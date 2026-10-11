from enum import Enum
from typing import Literal


# Sentinel marking a field that was omitted
# Different from None which clears the field
class Sentinel(Enum):
    UNSET = "UNSET"


UNSET = Sentinel.UNSET
type Unset = Literal[Sentinel.UNSET]