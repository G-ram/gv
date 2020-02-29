from .bit import bit

class reg(object):
	def __init__(self, width):
		# Elaborate here
		self.__impl__()

	def __impl__(self):
		self.clk = bit(1)
		self.rst_l = bit(1)
		self.en = bit(1)
		self.clear = bit(1)
		self.D = bit(width)
		self.Q = bit(width)