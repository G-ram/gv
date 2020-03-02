from io import StringIO
import bit
import stream
import elaborate

class reg(object):
	var_count = 0
	def __init__(self, width=1, rst_value=None, name=None):
		# Elaborate here
		self.name = name
		if self.name is None:
			self.name = 'r%d' % var_count
			var_count += 1
		self.rst_value = rst_value
		self._width = width
		elaborate.ELABORATE.reg(self)
		self.impl()
		elaborate.ELABORATE.endreg()

	def impl(self):
		self.clk = bit.bit(1)
		self.rst_l = bit.bit(1)
		self.en = bit.bit(1)
		self.clear = bit.bit(1)
		self.D = bit.bit(self._width)
		self.Q = bit.bit(self._width)

	def __repr__(self):
		s = StringIO()
		f = stream.stream(s)
		f.write('register #(%d' % self._width)
		if self.rst_value is not None:
			f.write(", 'd%d" % (self._width, self.rst_value))
		f.write(') (.clk, .rst_l,\n')
		f.indent()
		f.writenl('.en(%s)' % self.en.__repr__())
		f.writenl('.clear(%s)' % self.en.__repr__())
		f.writenl('.en(%s)' % self.en.__repr__())
		f.writenl('.D(%s)' % self.D.__repr__)
		f.writenl('.Q(%s));' % self.Q.__repr__)
		f.unindent()
		return s.getvalue()