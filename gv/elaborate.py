class elaborate(object):
	def __init__(self):
		pass

	def bit(self):
		pass

	def reg(self):
		pass

	def struct(self, name):
		pass

	def union(self, name):
		pass

	def port(self, input=False):
		pass

	def module(self, name):
		pass

	def connect(self):
		pass

	def conditional(self):
		pass

	def trinary(self):
		pass

	def binary(self):
		pass

	def unary(self):
		pass

	def concat(self):
		pass

	def dump(self, stream):
		stream.writenl('DUMP')

	def bits(self):
		return 0

ELABORATE = elaborate()