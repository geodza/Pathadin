from slide_viewer.ui.slide.widget.interface.mdi_sub_window_service import SubWindowService


def on_add_sub_window(s: SubWindowService) -> None:
    w=s.add_sub_window()
    w.show()
    s.tile_sub_windows()

