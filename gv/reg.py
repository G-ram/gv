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
		self.w = width
		elaborate.ELABORATE.reg(self)
		self.__impl__()
		elaborate.ELABORATE.endreg()

	def __impl__(self):
		self.clk = bit.bit(1)
		self.rst_l = bit.bit(1)
		self.en = bit.bit(1)
		self.clear = bit.bit(1)
		self.D = bit.bit(self.w)
		self.Q = bit.bit(self.w)

	def __repr__(self):
		s = StringIO()
		f = stream.stream(s)
		f.write('register #(%d' % self.w)
		if self.rst_value is not None:
			f.write(", 'd%d" % (self.w, self.rst_value))
		f.write(') (.clk, .rst_l,\n')
		f.indent()
		f.writenl('.en(%s)' % self.en.__repr__())
		f.writenl('.clear(%s)' % self.en.__repr__())
		f.writenl('.en(%s)' % self.en.__repr__())
		f.writenl('.D(%s)' % self.D.__repr__)
		f.writenl('.Q(%s));' % self.Q.__repr__)
		f.unindent()
		return s.getvalue()