from io import StringIO
import stream
import elaborate
import bit

class module(object):
	class metadata(object):
		def __init__(self):
			self.name = None
			self.types = {}
			self.decls = {}
			self.blocks = []
			self.insts = []
			self.regs = []

	def __init__(self):
		self._gvim = module.metadata()
		self.ref = None
		self.ref = elaborate.ELABORATE.module(self)
		if self.ref is None:
			elaborate.ELABORATE.endmodule(self)

	def name(self):
		if self.ref is not None:
			return self.ref.name()
		return self.__class__.__name__

	def types(self):
		if self.ref is not None:
			return self.ref.types()
		return self._gvim.types

	def append_type(self, t):
		if self.ref is not None:
			self.ref.append_type(t)
		self._gvim.types[t.typename()] = t

	def decls(self):
		if self.ref is not None:
			return self.ref.decls()
		return self._gvim.decls

	def append_decl(self, decl):
		if self.ref is not None:
			self.ref.append_dec(decl)
		self._gvim.decls[decl.name()] = decl

	def blocks(self):
		if self.ref is not None:
			return self.ref.blocks()
		return self._gvim.blocks

	def append_block(self, block):
		if self.ref is not None:
			self.ref.append_block(block)
		self._gvim.blocks.append(block)

	def insts(self):
		if self.ref is not None:
			return self.ref.insts()
		return self._gvim.insts

	def append_inst(self, inst):
		if self.ref is not None:
			return self.ref.append_inst(inst)
		self._gvim.insts.append(inst)

	def regs(self):
		if self.ref is not None:
			return self.ref.regs()
		return self._gvim.regs

	def append_reg(self, reg):
		if self.ref is not None:
			self.ref.append_reg(reg)
		self._gvim.regs.append(reg)

	def impl(self):
		raise NotImplementedError()

	def __getattr__(self, v):
		ref = super().__getattribute__('ref')
		attr = None
		if ref is not None:
			attr = ref.__getattribute__(v)
		else:
			attr = super().__getattribute__(v)
		if v != 'ref' and isinstance(attr, bit.bit):
			pass
		return attr

	def __repr__(self):
		s = StringIO()
		f = stream.stream(s)
		f.writenl('module %s(' % self.name())
		f.indent()
		ports = []
		prev_port = False
		decls = self.decls()
		for k in decls:
			p = decls[k]
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

		decls = self.decls()
		for k in decls:
			p = decls[k]
			if p.__repr__() not in ports and not p.const():
				f.writenl(p.__declare_repr__())

		for i in self.insts():
			decls = i.module().decls()
			for k in decls:
				p = decls[k]
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
