from threading import Timer
from typing import Callable, Optional


def debounce_time(wait_sec: float, func: Callable) -> Callable:
	# https://tsilva.me/how-to-write-a-debouncer-function-in-python/
	"""Returns a debounced version of a function.

	The debounced function delays invoking `func` until after `wait`
	seconds have elapsed since the last time the debounced function
	was invoked.
	"""
	scheduled_timer: Optional[Timer] = None

	def debounced_func(*args, **kwargs):
		nonlocal scheduled_timer
		if scheduled_timer and not scheduled_timer.finished.is_set():
			print(f'canceling {func} {scheduled_timer}')
			scheduled_timer.cancel()
		scheduled_timer = Timer(wait_sec, func, args=args, kwargs=kwargs)
		scheduled_timer.start()

	return debounced_func


def debounce(wait_sec: float) -> Callable:
	def debounce_(func):
		return debounce_time(wait_sec, func)

	return debounce_
