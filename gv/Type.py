from io import StringIO
import bit
import stream
import elaborate

class Type(bit.bit):
	def __init__(self, value=None, name=None, ref=None):
		self._gvim = []
		self.ref = ref
		if ref is None:
			self.ref = elaborate.ELABORATE.typedef(self.typename())
			if self.ref is None:
				self.impl()
				self._gvim = elaborate.ELABORATE.endtypedef(self)	
		super().__init__(self.width(), value, name)

	def __getattr__(self, v):
		ref = super().__getattribute__('ref')
		attr = None
		if ref is not None:
			attr = ref.__getattribute__(v)
		else:
			attr = super().__getattribute__(v)
		if v != 'ref' and isinstance(attr, bit.bit):
			import expr
			return expr.dot_expr(self, attr)
		return attr

	def clone(self):
		return Type(self.value(), None, self if self.ref is None else self.ref)

	def typename(self):
		if self.ref is not None:
			return self.ref.typename()
		return self.__class__.__name__

	def members(self):
		if self.ref is not None:
			return self.ref._gvim
		return self._gvim

	def set_members(self, *args):
		if self.ref is not None:
			self.ref._gvim = [a for a in args]
		self._gvim = [a for a in args]

	def __repr__(self):
		return self.name()

	def __declare_repr__(self):
		if self.dxn() is not None:
			return super().__declare_repr__()

		rep = '%s %s;' % (self.typename(), self.name())
		return rep

	def __define_repr__(self):
		s = StringIO()
		f = stream.stream(s)
		for member in self.members():
			f.writenl(member.__declare_repr__())	
		return s.getvalue()

class union(Type):
	def width(self):
		if len(self.members()) == 0:
			raise ValueError
		return max(map(lambda x: x.width(), self.members())) 

	def __define_repr__(self):
		s = StringIO()
		f = stream.stream(s)
		f.writenl('typedef union packed {')
		f.indent()
		for line in super().__define_repr__().splitlines():
			f.writenl(line)	
		f.unindent()
		f.writenl('} %s;' % self.typename())
		return s.getvalue()	

class Struct(Type):
	def width(self):
		if len(self.members()) == 0:
			raise ValueError
		return sum(map(lambda x: x.width(), self.members())) 

	def __define_repr__(self):
		s = StringIO()
		f = stream.stream(s)
		f.writenl('typedef struct packed {')
		f.indent()
		for line in super().__define_repr__().splitlines():
			f.writenl(line)	
		f.unindent()
		f.writenl('} %s;' % self.typename())
		return s.getvalue()	