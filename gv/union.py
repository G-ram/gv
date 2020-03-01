from io import StringIO
import bit
import stream
import elaborate

class union(bit.bit):
	def __init__(self, value=None, name=None):
		self.value = value
		self.type_name = self.__class__.__name__ 
		elaborate.ELABORATE.typedef(self)
		self.__impl__()
		self.members = elaborate.ELABORATE.endtypedef(self)
		self.name = name
		if self.name is None:
			self.name = 'v%d' % bit.bit.var_count
			bit.bit.var_count +=1

		elaborate.ELABORATE.declare(self)
		self.w = max(map(lambda x: x.width(), self.members))
		self.dimensions = [self.w]

	def width(self):
		self.w = max(map(lambda x: x.width(), self.members))
		return self.w

	def __impl__(self):
		raise NotImplementedError()

	def __repr__(self):
		return self.name

	def __define_repr__(self):
		s = StringIO()
		f = stream.stream(s)
		f.writenl('typdef union packed {')
		f.indent()
		for member in self.members:
			f.writenl(member.__declare_repr__())	
		f.unindent()
		f.writenl('} %s;' % self.type_name)
		return s.getvalue()