import sys
from threading import Timer
from typing import TypeVar, Generic, Callable, Any

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QObject, QTimer
from PyQt5.QtWidgets import QApplication
from typing_extensions import Protocol

from common.debounce import debounce_time
from common_qt.util.message_handler import qt_message_handler

S = TypeVar('S')
T = TypeVar('T')


class QtSignal(Protocol, Generic[S]):
	def connect(self, f: Callable[[S], Any]):
		pass


class QtSignalContainer(QObject):
	signal = pyqtSignal(object)


# def pipe_signal(signal: QtSignal[S], op: Callable[ [QtSignal[S]], QtSignal[T]]) -> QtSignal[T]:
# 	new_signal_container = QtSignalContainer()
#
# 	def on_signal(value: S = None):
# 		new_value = op(value)
# 		new_signal_container.signal.emit(new_value)
#
# 	signal.connect(on_signal)
# 	return new_signal_container.signal
#


def pipe_map(signal: QtSignal[S], op: Callable[[S], T]) -> QtSignal[T]:
	new_signal_container = QtSignalContainer()

	def on_signal(value: S = None):
		new_value = op(value)
		new_signal_container.signal.emit(new_value)

	signal.connect(on_signal)
	return new_signal_container.signal


def throttle_time(wait_sec: float) -> Callable[[S], S]:
	scheduled_timer = None

	def emit_new_signal(*args,**kwargs):


	def debounced_func(*args, **kwargs):
		nonlocal scheduled_timer
		if scheduled_timer and not scheduled_timer.finished.is_set():
			# print(f'canceling {func} {scheduled_timer}')
			scheduled_timer.cancel()
		scheduled_timer = Timer(wait_sec, func, args=args, kwargs=kwargs)
		scheduled_timer.start()

	return debounced_func
	def op_(s: S) -> S:
		return s

	return debounce_time(wait_sec, op_)


class A(QObject):
	signal1 = pyqtSignal(int)


if __name__ == '__main__':
	# a = A()
	#
	#
	# def on_a(v):
	# 	print(v)
	#
	#
	# a.signal1.connect(on_a)
	# a.signal1.emit(1)
	#
	# pipe_signal(a.signal1, lambda x: x * 2).connect(on_a)
	# a.signal1.emit(1)
	QtCore.qInstallMessageHandler(qt_message_handler)

	app = QApplication(sys.argv)

	timer = QTimer()
	timer.setInterval(1000)
	timer.timeout.connect(lambda: print("timeout"))
	pipe_signal(timer.timeout, throttle_time(2)).connect(lambda: print("only each 2 sec"))
	timer.start()
	sys.exit(app.exec_())
