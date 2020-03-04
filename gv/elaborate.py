import stmt

class elaborate(object):
	class metadata(object):
		def __init__(self):
			self.module = None
			self.blocks = None
			self.disable_declare = None

	def __init__(self):
		self.modules = {}
		self.blocks = []
		self.cmodule = None
		self.cblock = None
		self.disable_declare = 0
		self.members = []
		self.finish_elaborate = []

	def dump(self, s):
		for key in self.modules:
			self.cmodule = self.modules[key]
			s.write(self.modules[key].__repr__())
			s.blank()

	def module(self, m):
		if self.cmodule is not None:
			self.cmodule.append_inst(stmt.inst_stmt(m))

		if m.name() in self.modules.keys():
			return self.modules[m.name()]

		return None

	def endmodule(self, m):
		if m.name() in self.modules.keys():
			return self.modules[m.name()]

		if self.cmodule is not None:
			# Save blocks, disable_declare
			metadata = elaborate.metadata()
			metadata.disable_declare = self.disable_declare
			metadata.module = self.cmodule
			metadata.blocks = [block for block in self.blocks]
			self.finish_elaborate.append(metadata)

			# Start elaboration
			self.blocks = []
			self.members = []
			self.disable_declare = 0
			self.cmodule = m
			self.cmodule.append_block(stmt.block_stmt())
			self.blocks.append(self.cmodule.blocks()[-1])
			self.cblock = self.blocks[-1]
			self.cmodule.impl()
			self.modules[m.name()] = m

			# Finish other modules
			if len(self.finish_elaborate) > 0:
				metadata = self.finish_elaborate.pop()
				self.blocks = metadata.blocks
				self.cmodule = metadata.module
				self.disable_declare = metadata.disable_declare
				self.cblock = self.blocks[-1]
		else:
			self.cmodule = m
			self.blocks = []
			self.members = []
			self.cmodule.append_block(stmt.block_stmt())
			self.blocks.append(self.cmodule.blocks()[-1])
			self.cblock = self.blocks[-1]
			self.cmodule.impl()
			self.modules[m.name()] = m

	def typedef(self, t):
		if t in self.cmodule.types().keys():
			return self.cmodule.types()[t]
		self.disable_declare += 1
		return None

	def endtypedef(self, t):
		if t.typename() in self.cmodule.types().keys():
			return self.cmodule.types()[t.typename()].members()
		self.disable_declare -= 1
		self.cmodule.append_type(t)
		members = [member for member in self.members]
		self.members = []
		return members

	def block(self):
		self.blocks.append(stmt.block_stmt())
		self.cblock = self.blocks[-1]

	def endblock(self):
		if len(self.blocks) == 0:
			raise IndexError
		return self.blocks.pop()

	def stmt(self, s):
		self.cblock.append_stmt(s)

	def declare(self, d):
		if self.disable_declare == 0 and \
			d.name() not in self.cmodule.decls().keys():
			self.cmodule.append_decl(d)
			return
		self.members.append(d)

ELABORATE = elaborate()