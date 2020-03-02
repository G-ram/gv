import statement

class elaborate(object):
	def __init__(self):
		self.modules = {}
		self.cmodule = None
		self.blocks = []
		self.cblock = None
		self.disable_declare = 0
		self.members = []
		self.elaborating_module = False
		self.need_to_elaborate = []

	def dump(self, s):
		for key in self.modules:
			s.write(self.modules[key].__repr__())
			s.blank()

	def module(self, m):
		if m.name not in self.modules.keys() and not self.elaborating_module:
			self.elaborating_module = True
			self.modules[m.name] = m
			self.cmodule = m
			self.blocks = []
			self.members = []
			self.cmodule.blocks.append(statement.block_stmt())
			self.blocks.append(self.cmodule.blocks[-1])
			self.cblock = self.blocks[-1]
			self.cmodule.__impl__()
			self.elaborating_module = False
			if len(self.need_to_elaborate) > 0:
				self.module(self.need_to_elaborate.pop(0))
		else:
			self.cmodule.instantiations.append(statement.inst_stmt(m))
			self.need_to_elaborate.append(m)

	def reg(self, r):
		self.cmodule.registers.append(r)
		self.disable_declare += 1

	def endreg(self, r):
		self.disable_declare -= 1

	def typedef(self, t):
		if t.type_name in self.cmodule.types.keys():
			return
		self.disable_declare += 1

	def endtypedef(self, t):
		if t.type_name in self.cmodule.types.keys():
			return self.cmodule.types[t.type_name].members
		self.cmodule.types[t.type_name] = t
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