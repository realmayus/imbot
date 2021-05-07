import dataclasses
from enum import Enum
from typing import Dict, Union, List


class Align(Enum):
    LEFT = 'left'
    CENTER = 'center'
    RIGHT = 'right'


@dataclasses.dataclass
class TextField:
    posX: int
    posY: int
    width: int
    height: int
    align: Align
    color: str
    font_size: float
    bold: bool


@dataclasses.dataclass
class ImageField:
    posX: int
    posY: int
    file: str


@dataclasses.dataclass
class Template:
    name: str
    labels: List[str]
    file: str
    id: str
    creator: int
    createdAt: int
    fields: Dict[str, List[Union[TextField, ImageField]]]
