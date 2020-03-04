import bit

class expr(bit.bit):
	def __init__(self, width, value, name):
		super().__init__(width, value, name)

	def compound(self):
		return True

class bin_op(expr):
	def __init__(self, op1, op2, operator):
		self.operator = operator
		self.op1 = op1
		self.op2 = op2
		super().__init__(min(self.op1.width(), self.op2.width()), None, None)

	def __repr__(self):
		return '(%s %s %s)' % (
			self.op1.__repr__(), self.operator, self.op2.__repr__())

class unary_op(expr):
	def __init__(self, op, operator):
		self.operator = operator
		self.op = op
		self.value = None
		super().__init__(op.width(), None, None)

	def __repr__(self):
		return '(%s%s)' % (self.operator, self.op.__repr__())

class list_op(expr):
	def __init__(self, *args):
		self.ops = [op for op in args]
		self.value = None
		super().__init__(sum(map(lambda x: x.width, self.ops)), None, None)

	def __repr__(self):
		rep = '{'
		for op in self.op:
			rep += '%s,' % op.__repr__()
		return '%s}' % rep[-1]

class bracket_expr(expr):
	def __init__(self, op, low, high):
		self.op = op
		self.low = low
		self.high = high
		self.value = None
		super().__init__(high - low if high else 1, None, None)

	def __repr__(self):
		if self.high is None:
			return '%s[%s]' % (self.op.__repr__(), self.low.__repr__())
		return '%s[%s:%s]' % (
			self.op.__repr__(), self.high.__repr__(), self.low.__repr__())

# What happens with several dot expressions in a row
class dot_expr(expr):
	def __init__(self, obj, mem):
		self.obj = obj
		self.mem = mem
		super().__init__(self.mem.width(), None, None)

	def __getattribute__(self, v):
		try:
			return super().__getattribute__(v)
		except AttributeError:
			return dot_expr(self, getattr(mem, v))

	def __repr__(self):
		return '%s.%s' % (self.obj.__repr__(), self.mem.__repr__())

class assign_expr(expr):
	def __init__(self, dest, src):
		self.dest = dest
		self.src = bit.conv(dest.width(), src)
		self.value = self.src.value
		super().__init__(self.dest.width(), None, None)

	def __repr__(self):
		return '%s = %s' % (self.dest.__repr__(), self.src.__repr__())