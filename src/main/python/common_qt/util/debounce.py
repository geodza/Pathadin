from functools import wraps
from typing import Callable

from PyQt5.QtCore import QTimer


def qt_debounce_time(wait_sec: float, func: Callable) -> Callable:
	scheduled_timer = QTimer()
	scheduled_timer.setSingleShot(False)
	scheduled_timer.setInterval(int(wait_sec * 1000))
	callback_attr = '__debounced_callback'

	def cancel(*args, **kwargs):
		if scheduled_timer.isActive() and hasattr(scheduled_timer, callback_attr):
			# print(f'canceling {func} {scheduled_timer}')
			scheduled_timer.stop()
			scheduled_timer.timeout.disconnect(getattr(scheduled_timer, callback_attr))
			delattr(scheduled_timer, callback_attr)

	# Standard python Timer is a thread instance.
	# And many actions (like editing item models) in Qt should be done only from main gui-thread.
	# So QTimer instead of simple Timer is important.
	# MUST BE CALLED ONLY FROM MAIN GUI-THREAD.
	# To make it thread-safe, one can create many single-shot QTimers, or synchronize one QTimer with lock.

	@wraps(func)
	def debounced_func(*args, **kwargs):
		cancel()

		def on_func():
			# print(f'on_func {func} {scheduled_timer}')
			scheduled_timer.stop()
			scheduled_timer.timeout.disconnect(getattr(scheduled_timer, callback_attr))
			delattr(scheduled_timer, callback_attr)
			func(*args, **kwargs)

		setattr(scheduled_timer, callback_attr, on_func)
		scheduled_timer.timeout.connect(on_func)
		scheduled_timer.start()

	return debounced_func


def qt_debounce(wait_sec: float) -> Callable:
	def debounce_(func):
		return qt_debounce_time(wait_sec, func)

	return debounce_
