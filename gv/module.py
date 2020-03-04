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

	def __init__(self):
		self._gvic = {}
		self._gvimap = {}
		self._gvicmap= {}
		self._gvim = module.metadata()
		self.ref = None
		self.ref = elaborate.ELABORATE.module(self)
		if self.ref is None:
			elaborate.ELABORATE.endmodule(self)

	def name(self):
		if self.ref is not None:
			return self.ref.name()
		return self.__class__.__name__

	def cxnname(self, name):
		return self._gvimap[name]

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

	def impl(self):
		raise NotImplementedError()

	def __getattribute__(self, v):
		ref = super().__getattribute__('ref')
		attr = None
		if ref is not None and v != '__inst_repr__' and v != 'cxnname' and \
			v != '_gvic' and v != '_gvimap':
			attr = ref.__getattribute__(v)
		else:
			attr = super().__getattribute__(v)
		if v != 'ref' and isinstance(attr, bit.bit) and \
			type(self) != type(elaborate.ELABORATE.cmodule):
			if v not in self._gvic:
				clone = attr.clone()
				self._gvic[v] = clone
				if ref is None:
					self._gvimap[attr.name()] = clone
					self._gvicmap[clone.name()] = attr.name()
				else:
					self._gvimap[self._gvicmap[attr.name()]] = clone
					self._gvicmap[clone.name()] = self._gvicmap[attr.name()]
					del self._gvicmap[attr.name()]
			return self._gvic[v]
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

		if len(self.decls()) > 0:
			f.blank()

		f.writenl('always_comb')
		for b in self.blocks():
			f.writenl(b.__repr__())

		inst_count = 0
		for i in self.insts():
			f.writenl(i.__inst_repr__(inst_count))
			inst_count += 1

		f.writenl('endmodule : %s' % self.name())
		return s.getvalue()

	def __inst_repr__(self, id):
		s = StringIO()
		f = stream.stream(s)
		f.write('%s %s%s(' % (self.name(), self.name(), id))
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
				f.write(p.__cxn_repr__(self._gvimap[p.name()]))
				more_than_one = True

		f.unindent()
		f.writenl(');')

		return s.getvalue()

