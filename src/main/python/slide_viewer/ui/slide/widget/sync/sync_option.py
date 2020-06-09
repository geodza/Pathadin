from enum import unique, Enum, auto


@unique
class SyncOption(Enum):
    all = auto()
    view_transform = auto()
    grid_visible = auto()
    grid_size = auto()
    file_path = auto()
    background_brush = auto()
    annotations = auto()
    annotation_filter = auto()

    @staticmethod
    def single_options():
        return set(SyncOption) - {SyncOption.all}