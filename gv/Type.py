from io import StringIO
import bit
import stream
import elaborate

class Type(bit.bit):
	class metadata(object):
		def __init__(self):
			self.members = []
			self.ref = None

	def __init__(self, value=None, name=None):
		self._gvit = Type.metadata()
		self._gvit.ref = self
		ref = elaborate.ELABORATE.typedef(self)
		if ref is None:
			self.impl()
		else:
			self._gvit.ref = ref
		self._gvit.members = elaborate.ELABORATE.endtypedef(self)	
		super().__init__(self.width(), value, name)

	def __getattr__(self, v):
		print('Type dot_access', v)
		return None

	def ref(self):
		return self._gvit.ref

	def typename(self):
		return self.__class__.__name__

	def members(self):
		return self.ref()._gvit.members

	def set_members(self, *args):
		self.ref()._gvit.members = [a for a in args]

	def __repr__(self):
		return self.name()

	def __define_repr__(self):
		s = StringIO()
		f = stream.stream(s)
		for member in self.members():
			f.writenl(member.__declare_repr__())	
		return s.getvalue()

class union(Type):
	def width(self):
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