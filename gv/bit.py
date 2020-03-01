import elaborate

class bit(object):
	var_count = 0
	def __init__(self, width=1, value=None, name=None):
		self.w = width
		self.value = value
		self.name = name
		if self.name is None:
			self.name = 'v%d' % bit.var_count
			bit.var_count += 1
		self.dxn = None
		self.dimensions = [width]
		elaborate.ELABORATE.declare(self)

	def const(self):
		return self.value is not None

	def width(self):
		return self.w

	def __call__(self, width):
		self.w *= width
		self.dimensions.append(width)
		return self

	def __declare_repr__(self):
		rep = ''
		if self.dxn == 1:
			rep = 'output '
		elif self.dxn == 0:
			rep = 'input '
		rep += 'logic '

		for d in self.dimensions:
			rep += '[%d:0]' % (d - 1)
		rep += ' %s;' % self.name
		return rep

	def __repr__(self):
		if self.value is not None:
			return "%d'd%d" % (self.w, self.value)
		return self.name

	# Helper functions
	def __conv(width, operand):
		if isinstance(operand, bit):
			return operand
		if isinstance(operand, int): 
			return bit(width, operand)
		raise TypeError

	def __make_bin_op(op1, op2, operator):
		if op1.const() and op2.const():
			return bit(min(op1.width(), op2.width()), eval('op1.value%sop2.value' % operator))
		return bin_op(op1, op2, operator)

	def __make_unary_op(op, operator):
		if op.const():
			return bit(op.width, eval('%sop.value' % operator))
		return unary_op(op, operator)

	def __make_get_expr(op, low, high=None):
		return get_expr(op, low, high)

	# Overloads
	def __getitem__(self, key):
		if isinstance(key, slice):
			s = bit.__conv(self.w, key.start)
			e = bit.__conv(self.w, key.stop)

			if self.const() and s.const() and e.const():
				start = s.value if s.value >= 0 else self.w - s.value
				stop = e.value if e.value >= 0 else self.w - e.value
				value = self.value >> start & ((1 << stop) - 1)
				return bit(stop - start, value)

			if s.const() and e.const():
				start = s.value if s.value >= 0 else self.w - s.value
				stop = e.value if e.value >= 0 else self.w - e.value
				return bit.__make_get_expr(self, start, stop)

			if e.const():
				stop = e.value if e.value >= 0 else self.w - e.value
				return bit.__make_get_expr(self, s, stop)

		s = bit.__conv(self.w, key)
		if self.const() & s.const():
			start = s.value if s.value >= 0 else self.w - s.value
			return bit(1, (self.value >> start) & 0x1)

		if s.const():
			start = s.value if s.value >= 0 else self.w - s.value
			return bit.__make_get_expr(self, start)

		return bit.__make_get_expr(self, s, None)

	def __add__(self, other):
		return bit.__make_bin_op(self, bit.__conv(self.w, other), '+')

	def __radd__(self, other):
		return self.__add__(other)

	def __sub__(self, other):
		return bit.__make_bin_op(self, bit.__conv(self.w, other), '-')

	def __rsub__(self, other):
		return bit.__make_bin_op(bit.__conv(self.w, other), self, '-')

	def __mul__(self, other):
		return bit.__make_bin_op(self, bit.__conv(self.w, other), '*')

	def __rmul__(self, other):
		return self.__mul__(other)

	def __lshift__(self, other):
		return bit.__make_bin_op(self, bit.__conv(self.w, other), '<<')

	def __rlshift__(self, other):
		return bit.__make_bin_op(bit.__conv(self.w, other), self, '<<')

	def __rshift__(self, other):
		return bit.__make_bin_op(self, bit.__conv(self.w, other), '>>')

	def __rrshift__(self, other):
		return bit.__make_bin_op(bit.__conv(self.w, other), self, '>>')

	def __or__(self, other):
		return bit.__make_bin_op(self, bit.__conv(self.w, other), '|')

	def __ror__(self, other):
		return self.__or__(other)

	def __xor__(self, other):
		return bit.__make_bin_op(self, bit.__conv(self.w, other), '^')

	def __rxor__(self, other):
		return self.__xor__(other)

	def __and__(self, other):
		return bit.__make_bin_op(self, bit.__conv(self.w, other), '&')

	def __rand__(self, other):
		return self.__and__(other)

	def __invert__(self):
		return bit.__make_unary_op(self, '~')

	def redor(self):
		return bit.__make_unary_op(self, '|')

	def redxor(self):
		return bit.__make_unary_op(self, '^')

	def redand(self):
		return bit.__make_unary_op(self, '&')

	def __lt__(self, other):
		return bit.__make_bin_op(self, bit.__conv(self.w, other), '<')

	def __gt__(self, other):
		return bit.__make_bin_op(self, bit.__conv(self.w, other), '>')

	def __le__(self, other):
		return bit.__make_bin_op(self, bit.__conv(self.w, other), '<=')

	def __ge__(self, other):
		return bit.__make_bin_op(self, bit.__conv(self.w, other), '>=')

	def __eq__(self, other):
		return bit.__make_bin_op(self, bit.__conv(self.w, other), '==')

	def __ne__(self, other):
		return bit.__make_bin_op(self, bit.__conv(self.w, other), '!=')

class bin_op(bit):
	def __init__(self, op1, op2, operator):
		self.operator = operator
		self.op1 = op1
		self.op2 = op2
		self.w = min(op1.width(), op2.width())
		self.value = None

	def __repr__(self):
		return '(%s%s%s)' % (
			self.op1.__repr__(), self.operator, self.op2.__repr__())

class unary_op(bit):
	def __init__(self, op, operator):
		self.operator = operator
		self.op = op
		self.w = op.width()
		self.value = None

	def __repr__(self):
		return '(%s%s)' % (str(self.operator.__repr__()), self.op.__repr__())

class list_op(bit):
	def __init__(self, *args):
		self.ops = [op for op in args]
		self.w = sum(map(lambda x: x.width, self.ops))
		self.value = None

	def __repr__(self):
		rep = '{'
		for op in self.op:
			rep += '%s,' % op.__repr__()
		return '%s}' % rep[-1]

class get_expr(bit):
	def __init__(self, op, low, high):
		self.op = op
		self.low = low
		self.high = high
		self.w = 1
		self.value = None
		if high is not None:
			self.w = high - low

	def __repr__(self):
		if self.high is None:
			return '(%s[%s])' % (self.op.__repr__(), self.low.__repr__())
		return '(%s[%s:%s])' % (
			self.op.__repr__(), self.high.__repr__(), self.low.__repr__())

class assign_expr(bit):
	def __init__(self, dest, src):
		self.dest = dest
		self.src = src
		self.w = dest.width()
		self.value = src.value

	def __repr__(self):
		return '%s = %s' % (self.dest.__repr__(), self.src.__repr__())

def concat(*args):
	return list_op(args)

def ternary(condition, expr1, expr2):
	pass