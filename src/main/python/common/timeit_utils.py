from functools import wraps
from time import time


def timing(f):
	# https://stackoverflow.com/questions/1622943/timeit-versus-timing-decorator
	@wraps(f)
	def wrap(*args, **kw):
		ts = time()
		result = f(*args, **kw)
		te = time()
		# print('func:{} args:[{}, {}] took: {:2.4f} sec'.format(f.__name__, str(args)[:30], str(kw)[:30], te - ts))
		return result

	return wrap


def f():
	c = 0
	for i in range(10000000):
		c += 1


if __name__ == '__main__':
	timing(f)()
