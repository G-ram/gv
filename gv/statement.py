from io import StringIO
import stream
import elaborate
import bit


def connect(dest, src):
	return stmt(bit.assign_expr(dest, src))

class cond(object):
	def __init__(self, evaluated=False):
		self.evaluated = evaluated
		self.rep = cond_stmt()

	def IF(self, condition, body):
		expr = condition()
		if isinstance(expr, bit.bit):
			# Elaborate here
			elaborate.ELABORATE.block()
			body() 
			block = elaborate.ELABORATE.endblock()
			self.rep.if_cond = expr
			self.rep.if_block = block
			return self
		if expr:
			body()
			self.evaluated = True
			return self
		return self

	def ELIF(self, condition, body):
		if self.evaluated:
			return self

		expr = condition()
		if isinstance(expr, bit.bit):
			# Elaborate here
			elaborate.ELABORATE.block()
			body() 
			block = elaborate.ELABORATE.endblock()
			self.rep.elif_conds.append(expr)
			self.rep.elif_blocks.append(block)
			return cond()
		if expr:
			body()
			self.evaluated = True
			return self
		return self

	def ELSE(self, body):
		if self.evaluated:
			return self
		elaborate.ELABORATE.block()
		body() 
		block = elaborate.ELABORATE.endblock()
		self.rep.else_block = block 
		self.evaluated = True
		return self

indent_level = 0
class stmt(object):
	def __init__(self, expr):
		self.expr = expr
		elaborate.ELABORATE.stmt(self)

	def __repr__(self):
		return '%s%s;\n' % (indent_level * '\t', self.expr.__repr__())

class cond_stmt(object):
	def __init__(self):
		self.if_cond = None
		self.if_block = None
		self.elif_conds = []
		self.elif_blocks = []
		self.else_block = None
		elaborate.ELABORATE.stmt(self)

	def __repr__(self):
		s = StringIO()
		f = stream.stream(s)
		if self.if_cond is not None:
			f.writenl('%sif%s ' % (
				indent_level * '\t', self.if_cond.__repr__()))
			f.write(self.if_block.__repr__())
			for i, elif_cond in enumerate(self.elif_conds):
				f.writenl('%selse if%s' % (
					indent_level * '\t', elif_cond.__repr__()))
				f.write(self.elif_blocks[i].__repr__())
			if self.else_block is not None:
				f.writenl('%selse' % (indent_level * '\t'))
				f.write(self.else_block.__repr__())
		elif len(self.elif_conds) > 0:
			f.writenl('%sif(%s) ' % (
				indent_level * '\t', self.elif_conds[0].__repr__()))
			f.write(self.elif_blocks[0].__repr__())
			for i, elif_cond in self.elif_conds:
				f.writenl('%selse if%s' % (
					indent_level * '\t', elif_cond.__repr__()))
				f.write(self.elif_blocks[i].__repr__())
			if self.else_block is not None:
				f.writenl('%selse' % (indent_level * '\t'))
				f.write(self.else_block.__repr__())
		elif self.else_block is not None:
			f.write(self.else_block.__repr__())
		return s.getvalue()

class inst_stmt(object):
	inst_count = 0
	def __init__(self, module):
		self.module = module
		self.name = 'inst%d' % inst_stmt.inst_count
		inst_stmt.inst_count += 1

	def __repr__(self):
		return '%s %s();' % (self.module.name(), self.name)

class block_stmt(object):
	def __init__(self, *args):
		self.stmts = [stmt for stmt in args]

	def append(self, stmt):
		self.stmts.append(stmt)
		return self

	def __repr__(self):
		global indent_level
		rep = '%sbegin\n' % (indent_level * '\t')
		indent_level += 1
		for stmt in self.stmts:
			rep += '%s' % stmt.__repr__()
		indent_level -= 1
		rep += '%send\n' % (indent_level * '\t')
		return rep
