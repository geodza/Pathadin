import sys

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QMdiArea, QMdiSubWindow

from common_qt.util.message_handler import install_qt_message_handler

if __name__ == "__main__":
    install_qt_message_handler()
    app = QApplication(sys.argv)
    window = QMainWindow()
    mdi = QMdiArea(window)
    mdi.setDocumentMode(True)
    mdi.setViewMode(QMdiArea.TabbedView)
    s1 = QMdiSubWindow(mdi)
    s1.setWindowTitle("mdi1")
    s1.setWidget(QLabel('1'))
    # mdi.addSubWindow(QLabel('1'))
    mdi.addSubWindow(QLabel('2'))
    mdi.addSubWindow(QLabel('3'))
    mdi.addSubWindow(QLabel('4'))
    mdi.tileSubWindows()

    window.setCentralWidget(mdi)

    window.show()
    window.resize(QSize(700, 700))
    sys.exit(app.exec_())
