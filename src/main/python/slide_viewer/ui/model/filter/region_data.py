import typing


class RegionData(typing.NamedTuple):
    img_path: str
    level: typing.Optional[int]
    origin_point: typing.Optional[typing.Tuple[int, int]]
    points: typing.Optional[typing.Tuple[typing.Tuple[int, int]]]