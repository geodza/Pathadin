from typing import Callable, Any

from PyQt5.QtCore import QObject, pyqtSignal


class Observable(QObject):
	signal = pyqtSignal(object)

	def pipe(self, op: Callable[['Observable'], 'Observable']) -> 'Observable':
		return op(self)

	def subscribe(self, s: Callable[[Any], None]) -> None:
		self.signal.connect(s)

	def next(self, o):
		self.signal.emit(o)


def pipe_map(op: Callable[[object], object]) -> Callable[[Observable], Observable]:
	def pipe__(obs: Observable) -> Observable:
		newobs = Observable()

		def pipe_(obj) -> Any:
			newobj = op(obj)
			newobs.signal.emit(newobj)

		obs.signal.connect(pipe_)
		return newobs

	return pipe__


def pipe_filter(op: Callable[[object], bool]) -> Callable[[Observable], Observable]:
	def pipe__(obs: Observable) -> Observable:
		newobs = Observable()

		def pipe_(obj) -> Any:
			newobj = op(obj)
			if newobj:
				newobs.signal.emit(obj)

		obs.signal.connect(pipe_)
		return newobs

	return pipe__


def pipe_distinct_until_changed(op: Callable[[object, object], bool]) -> Callable[[Observable], Observable]:
	def pipe__(obs: Observable) -> Observable:
		newobs = Observable()

		last_obj_wrap = {'PRISTINE_TOKEN': True, 'value': None}

		def pipe_(obj) -> Any:
			if last_obj_wrap['PRISTINE_TOKEN']:
				last_obj_wrap['PRISTINE_TOKEN'] = False
				last_obj_wrap['value'] = obj
				newobs.signal.emit(obj)
			else:
				last_obj = last_obj_wrap['value']
				changed = op(last_obj, obj)
				last_obj_wrap['value'] = obj
				if changed:
					newobs.signal.emit(obj)

		obs.signal.connect(pipe_)
		return newobs

	return pipe__


if __name__ == '__main__':
	o = Observable()
	# o.pipe(pipe_map(lambda x: x * 2)).subscribe(print)
	o.next(1)
	o.signal.emit(2)
	# o.pipe(pipe_filter(lambda x: x > 3)).subscribe(print)
	o.signal.emit(1)
	o.signal.emit(2)
	o.signal.emit(3)
	o.signal.emit(4)
	o.pipe(pipe_filter(lambda x: x > 3)) \
		.pipe(pipe_distinct_until_changed(lambda prev, curr: prev != curr)) \
		.subscribe(print)
	o.next(1)
	o.next(2)
	o.next(3)
	o.next(4)
	o.next(4)
	o.next(5)
	o.next(5)
	o.next(5)
	o.next(6)
	o.next(5)
	o.next(6)
	o.next(6)
	o.next(7)