import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QErrorMessage


def excepthook(excType, excValue, tracebackobj):
    print(excType, excValue, tracebackobj)


# https://stackoverflow.com/questions/35894171/redirect-qdebug-output-to-file-with-pyqt5
def qt_message_handler(mode, context, message):
    if mode == QtCore.QtInfoMsg:
        mode = 'INFO'
    elif mode == QtCore.QtWarningMsg:
        mode = 'WARNING'
    elif mode == QtCore.QtCriticalMsg:
        mode = 'CRITICAL'
        QErrorMessage().showMessage(f'{mode}: {message}')
    elif mode == QtCore.QtFatalMsg:
        mode = 'FATAL'
        QErrorMessage().showMessage(f'{mode}: {message}')
    else:
        mode = 'DEBUG'
    print('qt_message_handler: line: %d, func: %s(), file: %s' % (
        context.line, context.function, context.file))
    print('  %s: %s\n' % (mode, message))
    sys.stdout.flush()


