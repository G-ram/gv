import statement

class elaborate(object):
	def __init__(self):
		self.modules = {}
		self.cmodule = None
		self.blocks = []
		self.cblock = None
		self.disable_declare = 0
		self.members = []

	def dump(self, s):
		s.write(str(self.cmodule.__repr__())) # Works for single module right now

	def module(self, m):
		if m.name in self.modules.keys():
			return
		self.modules[m.name] = m
		self.cmodule = m
		self.cmodule.blocks.append(statement.block_stmt())
		self.blocks.append(self.cmodule.blocks[-1])
		self.cblock = self.blocks[-1]

	def endmodule(self):
		return # Does nothing right now

	def reg(self, r):
		self.cmodule.registers.append(r)
		self.disable_declare += 1

	def endreg(self, r):
		self.disable_declare -= 1

	def typedef(self, t):
		if t.type_name in self.cmodule.types.keys():
			return
		self.disable_declare += 1
		self.cmodule.types[t.type_name] = t

	def endtypedef(self, t):
		self.disable_declare -= 1
		members = [member for member in self.members]
		self.members = []
		return members

	def block(self):
		self.blocks.append(statement.block_stmt())
		self.cblock = self.blocks[-1]

	def endblock(self):
		if len(self.blocks) == 0:
			raise IndexError
		return self.blocks.pop()

	def stmt(self, s):
		self.cblock.append(s)

	def declare(self, d):
		if self.disable_declare == 0:
			self.cmodule.declarations.append(d)
			return
		self.members.append(d)

ELABORATE = elaborate()