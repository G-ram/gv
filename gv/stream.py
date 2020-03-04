class stream(object):
	def __init__(self, handle):
		self.handle = handle
		self.indent_level = 0

	def indent(self, i=1):
		self.indent_level += i

	def unindent(self, i=1):
		self.indent_level -= i
		if self.indent_level < 0:
			self.indent_level = 0

	def write(self, v='', i=-1):
		if i >= 0:
			self.handle.write('%s%s' % ('\t'*i, v))
		else:
			self.handle.write('%s%s' % ('\t'*self.indent_level, v))

	def blank(self):
		self.writenl('')

	def writenl(self, v='', i=-1):
		self.write('%s\n' % v, i)

	def close(self):
		self.handle.close()