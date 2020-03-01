from io import StringIO
import stream
import elaborate

class module(object):
	def __init__(self):
		self.types = {}
		self.ports = []
		self.declarations = []
		self.blocks = []
		self.registers = []
		self.name = self.__class__.__name__
		elaborate.ELABORATE.module(self)
		self.__impl__()
		elaborate.ELABORATE.endmodule()

	def __impl__(self):
		raise NotImplementedError()

	def __repr__(self):
		s = StringIO()
		f = stream.stream(s)
		f.writenl('module %s(' % self.name)
		f.indent()
		ports = []
		for p in self.declarations:
			if p.dxn is not None:
				ports.append(p)
				f.writenl(p.__declare_repr__())
		f.unindent()
		f.writenl(');')

		for k in self.types:
			f.writenl(self.types[k].__define_repr__())

		for d in self.declarations:
			if d not in ports:
				f.writenl(d.__declare_repr__())

		f.writenl('always_comb')
		for b in self.blocks:
			f.writenl(b.__repr__())

		for r in self.registers:
			f.writenl(r.__repr__())

		f.writenl('endmodule : %s' % self.name)
		return s.getvalue()
