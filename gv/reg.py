from io import StringIO
import bit
import module
import stream

class reg(module.module):
	def __init__(self, width=1, rst_value=None):
		self.rst_value = 0 if rst_value is None else rst_value
		self.w = width
		super().__init__()

	def width(self):
		return self.w

	def name(self):
		return 'register_%d_%d' % (self.width(), self.rst_value) 

	def impl(self):
		self.clk = bit.input(bit.bit(1))
		self.rst_l = bit.input(bit.bit(1))
		self.en = bit.input(bit.bit(1))
		self.clear = bit.input(bit.bit(1))
		self.D = bit.input(bit.bit(self.width()))
		self.Q = bit.output(bit.bit(self.width()))

	def __inst_repr__(self, id):
		s = StringIO()
		f = stream.stream(s)
		f.write('register #(%d, %d) REG%s(' % (
			self.width(), self.rst_value, id))
		more_than_one = False
		indented = False
		decls = self.decls()
		for k in decls:
			p = decls[k]
			if p.dxn() is not None:
				if more_than_one:
					f.writenl(',', i=0)
					if not indented:
						f.indent()
						indented = True
				f.write(p.__cxn_repr__(self.cxnname(p.name())))
				more_than_one = True

		f.unindent()
		f.writenl(');')

		return s.getvalue()

	def __repr__(self):
		return ''