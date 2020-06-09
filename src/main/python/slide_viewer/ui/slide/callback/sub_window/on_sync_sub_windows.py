from slide_viewer.ui.slide.widget.interface.mdi_sub_window_service import SubWindowService
from slide_viewer.ui.slide.widget.sync.sync_option import SyncOption


# def on_sync_sub_windows(s: SubWindowService, sync: bool) -> None:
#     s.set_sync(sync)


def on_sync_option(s: SubWindowService, sync_option: SyncOption, sync: bool) -> None:
    s.set_sync_state(sync_option, sync)
    if sync_option == SyncOption.all:
        for opt in SyncOption:
            s.set_sync_state(opt, sync)
    else:
        s.set_sync_state(SyncOption.all, all([s.get_sync_state(opt) for opt in SyncOption.single_options()]))
