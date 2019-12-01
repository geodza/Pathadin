from enum import Enum, auto


class AnnotationType(Enum):
    LINE = auto()
    RECT = auto()
    ELLIPSE = auto()
    POLYGON = auto()

    def has_area(self) -> bool:
        return self in {AnnotationType.RECT, AnnotationType.ELLIPSE, AnnotationType.POLYGON}

    def has_length(self):
        return self == AnnotationType.LINE
