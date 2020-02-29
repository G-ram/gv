from .elaborate import ELABORATE

class bit(object):
	def __init__(self, width=1, value=None):
		self.width = 1
		self.value = value
		# Elaborate here

	def __call__(self, width):
		return self

	def __getitem__(self, key):
		if isinstance(key, slice):
			pass
		return bit()

	def __setitem__(self, key):
		if isinstance(key, slice):
			pass
		return bit()

	def __add__(self, other):
		return bit()

	def __sub__(self, other):
		return bit()

	def __mul__(self, other):
		return bit()

	def __or__(self, other):
		return bit()

	def __xor__(self, other):
		return bit()

	def __and__(self, other):
		return bit()

	def __invert__(self):
		return bit()

	def __lt__(self, other):
		return bit()

	def __gt__(self, other):
		return bit()

	def __le__(self, other):
		return bit()

	def __ge__(self, other):
		return bit()

	def __eq__(self, other):
		return bit()

	def __ne__(self, other):
		return bit()

	def __lshift__(self, other):
		return bit()

	def __rshift__(self, other):
		return bit()

	def redor(self):
		return bit()

	def redxor(self):
		return bit()

	def redand(self):
		return bit() 

def concat(*args):
	pass

class cond(object):
	def __init__(self, evaluated=None):
		self.evaluated = evaluated

	def IF(self, condition, body):
		if isinstance(condition(), bit):
			# Elaborate here
			return cond()
		if(condition()):
			body()
			return cond(True)
		return cond(True)

	def ELIF(self, condition, body):
		if self.evaluated:
			return self

		if isinstance(condition(), bit):
			# Elaborate here
			return cond()
		if(condition()):
			body()
			return cond(True)
		return cond(False)

	def ELSE(self, body):
		if self.evaluated:
			return self
		if self.evaluated is None:
			# Elaborate here
			pass
		body()
		return cond(True)

def ternary(condition, expr1, expr2):
	if isinstance(condition(), bit):
		# elaborate
		expr1()
		expr2()
		return
	if cond():
		expr1()
		return
	expr2()
