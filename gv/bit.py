import elaborate

class bit(object):
	var_count = 0
	class metadata(object):
		def __init__(self):
			self.width = None
			self.value = None
			self.name = None
			self.dxn = None
			self.dim = None

	def __init__(self, width=1, value=None, name=None):
		self._gvi = bit.metadata()
		self._gvi.width = width
		self._gvi.value = value
		self._gvi.name = name
		if self._gvi.name is None and not self.const():
			self._gvi.name = 'gv%d' % bit.var_count
			bit.var_count += 1
		self._gvi.dxn = None
		self._gvi.dim = [self._gvi.width]
		if self.const() or self.compound():
			return
		elaborate.ELABORATE.declare(self)

	def clone(self):
		return bit(self.width(), None)

	def const(self):
		return self._gvi.value is not None

	def compound(self):
		return False

	def width(self):
		return self._gvi.width

	def set_width(self, width):
		self._gvi.width = width

	def dim(self):
		return self._gvi.dim

	def set_dim(self, *args):
		self._gvi.dim = [a for a in args]

	def append_dim(self, dim):
		self._gvi.dim.append(dim)

	def name(self):
		return self._gvi.name

	def value(self):
		return self._gvi.value

	def set_value(self, value):
		self._gvi.dxn = value

	def dxn(self):
		return self._gvi.dxn

	def set_dxn(self, dxn):
		self._gvi.dxn = dxn

	def __call__(self, width):
		self.set_width(self.width() * width)
		self.append_dim(width)
		return self

	def __declare_repr__(self):
		rep = ''
		dxn = self.dxn()
		if dxn == 1:
			rep = 'output '
		elif dxn == 0:
			rep = 'input '
		rep += 'logic '

		if self.width() > 1:
			for d in self.dim():
				rep += '[%d:0]' % (d - 1)
			rep += ' ' 
		rep += '%s;' % self.name()
		return rep

	def __declare_cxn_repr__(self):
		rep = 'logic '

		for d in self.dim():
			rep += '[%d:0]' % (d - 1)
		rep += ' %s;' % self.name()
		return rep

	def __cxn_repr__(self, name):
		return '.%s(%s)' % (self.name(), name)

	def __repr__(self):
		if self.value() is not None:
			return "%d'd%d" % (self.width(), self.value())
		return self.name()

	def __make_bin_op(op1, op2, operator):
		if op1.const() and op2.const():
			return bit(min(op1.width(), op2.width()), eval('op1.value()%sop2.value()' % operator))
		import expr
		return expr.bin_op(op1, op2, operator)

	def __make_unary_op(op, operator):
		if op.const():
			return bit(op.width, eval('%sop.value()' % operator))
		import expr
		return expr.unary_op(op, operator)

	def __make_bracket_expr(op, low, high=None):
		import expr
		return expr.bracket_expr(op, low, high)

	# Overloads
	def __getitem__(self, key):
		if isinstance(key, slice):
			s = conv(self.width(), key.start)
			e = conv(self.width(), key.stop)

			def get_idx(v):
				return v.value() if v.value() >= 0 else self.width() - v.value()

			if self.const() and s.const() and e.const():
				start = get_idx(s)
				stop = get_idx(e)
				value = self.value() >> start & ((1 << stop) - 1)
				return bit(stop - start, value)

			if s.const() and e.const():
				start = get_idx(s)
				stop = get_idx(e)
				return bit.__make_bracket_expr(self, start, stop)

			if e.const():
				stop = get_idx(e)
				return bit.__make_bracket_expr(self, s, stop)

		s = conv(self.width(), key)
		if self.const() & s.const():
			start = get_idx(s)
			return bit(1, (self.value() >> start) & 0x1)

		if s.const():
			start = get_idx(s)
			return bit.__make_bracket_expr(self, start)

		return bit.__make_bracket_expr(self, s, None)

	def __add__(self, other):
		return bit.__make_bin_op(self, conv(self.width(), other), '+')

	def __radd__(self, other):
		return self.__add__(other)

	def __sub__(self, other):
		return bit.__make_bin_op(self, conv(self.width(), other), '-')

	def __rsub__(self, other):
		return bit.__make_bin_op(conv(self.width(), other), self, '-')

	def __mul__(self, other):
		return bit.__make_bin_op(self, conv(self.width(), other), '*')

	def __rmul__(self, other):
		return self.__mul__(other)

	def __lshift__(self, other):
		return bit.__make_bin_op(self, conv(self.width(), other), '<<')

	def __rlshift__(self, other):
		return bit.__make_bin_op(conv(self.width(), other), self, '<<')

	def __rshift__(self, other):
		return bit.__make_bin_op(self, conv(self.width(), other), '>>')

	def __rrshift__(self, other):
		return bit.__make_bin_op(conv(self.width(), other), self, '>>')

	def __or__(self, other):
		return bit.__make_bin_op(self, conv(self.width(), other), '|')

	def __ror__(self, other):
		return self.__or__(other)

	def __xor__(self, other):
		return bit.__make_bin_op(self, conv(self.width(), other), '^')

	def __rxor__(self, other):
		return self.__xor__(other)

	def __and__(self, other):
		return bit.__make_bin_op(self, conv(self.width(), other), '&')

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
		return bit.__make_bin_op(self, conv(self.width(), other), '<')

	def __gt__(self, other):
		return bit.__make_bin_op(self, conv(self.width(), other), '>')

	def __le__(self, other):
		return bit.__make_bin_op(self, conv(self.width(), other), '<=')

	def __ge__(self, other):
		return bit.__make_bin_op(self, conv(self.width(), other), '>=')

	def __eq__(self, other):
		return bit.__make_bin_op(self, conv(self.width(), other), '==')

	def __ne__(self, other):
		return bit.__make_bin_op(self, conv(self.width(), other), '!=')

def output(handle):
	handle.set_dxn(1)
	return handle

def input(handle):
	handle.set_dxn(0)
	return handle

def conv(width, operand):
	if isinstance(operand, bit):
		return operand
	if isinstance(operand, int): 
		return bit(width, operand)
	raise TypeError
