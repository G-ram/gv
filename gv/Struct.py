from io import StringIO
import bit
import stream
import elaborate

class Struct(bit.bit):
	def __init__(self, value=None, name=None):
		self.value = value
		elaborate.ELABORATE.typedef(self)
		self.impl()
		self.members = elaborate.ELABORATE.endtypedef(self)
		self.name = name
		if self.name is None:
			self.name = 'gv%d' % bit.bit.var_count
			bit.bit.var_count +=1

		elaborate.ELABORATE.declare(self)
		self._width = sum(map(lambda x: x.width(), self.members))
		self._dim = [self._width]
		self._dxn = None

	def width(self):
		self._width = sum(map(lambda x: x.width(), self.members))
		return self._width

	def typename(self):
		return self.__class__.name 

	def impl(self):
		raise NotImplementedError()

	def __getattr__(self):
		pass

	def __repr__(self):
		return self.name

	def __define_repr__(self):
		s = StringIO()
		f = stream.stream(s)
		f.writenl('typedef struct packed {')
		f.indent()
		for member in self.members:
			f.writenl(member.__declare_repr__())	
		f.unindent()
		f.writenl('} %s;' % self.typename())
		return s.getvalue()