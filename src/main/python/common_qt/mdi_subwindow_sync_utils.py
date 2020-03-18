from PyQt5.QtWidgets import QMdiSubWindow


def sync_about_to_activate(w1: QMdiSubWindow, w2: QMdiSubWindow) -> None:
    w1.aboutToActivate.connect(lambda: w2.setFocus())
    w2.aboutToActivate.connect(lambda: w1.setFocus())


def sync_close(w1: QMdiSubWindow, w2: QMdiSubWindow) -> None:
    w1.aboutToClose.connect(lambda: w2.close())
    w2.aboutToClose.connect(lambda: w1.close())
