from io import StringIO
import stream
import elaborate

class module(object):
	class metadata(object):
		def __init__(self):
			self.name = None
			self.types = {}
			self.decls = []
			self.blocks = []
			self.insts = []
			self.regs = []

	def __init__(self):
		self._gvim = module.metadata()
		elaborate.ELABORATE.module(self)

	def name(self):
		return self.__class__.__name__

	def types(self):
		return self._gvim.types

	def append_type(self, t):
		self._gvim.types[t.typename()] = t

	def decls(self):
		return self._gvim.decls

	def append_decl(self, decl):
		self._gvim.decls.append(decl)

	def blocks(self):
		return self._gvim.blocks

	def append_block(self, block):
		self._gvim.blocks.append(block)

	def insts(self):
		return self._gvim.insts

	def append_inst(self, inst):
		self._gvim.insts.append(inst)

	def regs(self):
		return self._gvim.regs

	def append_reg(self, reg):
		self._gvim.regs.append(reg)

	def impl(self):
		raise NotImplementedError()

	def __getattr__(self, v):
		print('Module dot access', v)
		for decl in self.decls():
			print(self.name(), decl.dxn(), decl.name(), v)
			if decl.dxn() and decl.name() == v:
				return decl
		raise AttributeError 

	def __repr__(self):
		s = StringIO()
		f = stream.stream(s)
		f.writenl('module %s(' % self.name())
		f.indent()
		ports = []
		prev_port = False
		for p in self.decls():
			if p.dxn() is not None:
				if prev_port:
					f.unindent()
					f.writenl(',')
					f.indent()
				ports.append(p.__repr__())
				f.write(p.__declare_repr__()[:-1])
				prev_port = True
		f.unindent()
		f.writenl(');')
		f.blank()

		for k in self.types():
			f.writenl(self.types()[k].__define_repr__())

		for d in self.decls():
			if d.__repr__() not in ports and not d.const():
				f.writenl(d.__declare_repr__())

		for i in self.insts():
			for p in i.module().decls():
				if p.dxn() is not None:
					f.writenl(p.__declare_cxn_repr__())
		f.blank()

		f.writenl('always_comb')
		for b in self.blocks():
			f.writenl(b.__repr__())

		for i in self.insts():
			f.writenl(i.__repr__())

		for r in self.regs():
			f.writenl(r.__repr__())

		f.writenl('endmodule : %s' % self.name())
		return s.getvalue()
