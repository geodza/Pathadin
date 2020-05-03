from enum import Enum, auto


class AnnotationType(str, Enum):
	LINE = "LINE"
	RECT = "RECT"
	ELLIPSE = "ELLIPSE"
	POLYGON = "POLYGON"

	def has_area(self) -> bool:
		return self in {AnnotationType.RECT, AnnotationType.ELLIPSE, AnnotationType.POLYGON}

	def has_length(self):
		return self == AnnotationType.LINE


if __name__ == '__main__':
	print(AnnotationType.LINE.value)
	print(AnnotationType.LINE)
	print(str(AnnotationType.LINE))
