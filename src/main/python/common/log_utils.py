from functools import wraps


def log(enabled: bool = True):
	enabled = True

	def log_(f):
		@wraps(f)
		def wrap(*args, **kw):
			if enabled:
				print(f'func: {f.__name__} args: {args}, kwargs: {kw}')
			result = f(*args, **kw)
			return result

		return wrap

	return log_
