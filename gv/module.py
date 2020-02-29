from .elaborate import ELABORATE

class module(object):
	def __init__(self):
		# ELABORATE.module(self.__class__.__name__)
		# Elaborate here
		self.__impl__()

	def __impl__(self):
		raise NotImplementedError()

