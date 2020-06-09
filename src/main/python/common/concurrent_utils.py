from concurrent.futures._base import Future


def not_canceled_done_callback(callback):
	def on_done(f: Future):
		if not f.cancelled():
			callback()

	return on_done