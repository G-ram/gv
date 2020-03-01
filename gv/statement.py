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

class stmt(object):
	def __init__(self, expr):
		self.expr = expr
		elaborate.ELABORATE.stmt(self)

	def __repr__(self):
		rep = self.expr.__repr__()
		if len(rep) == 0:
			return ''
		return '%s;' % rep

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
			f.writenl('if%s ' % self.if_cond.__repr__())
			f.write(self.if_block.__repr__())
			for i, elif_cond in enumerate(self.elif_conds):
				f.writenl('else if%s' % elif_cond.__repr__())
				f.write(self.elif_blocks[i].__repr__())
			if self.else_block is not None:
				f.writenl('else')
				f.write(self.else_block.__repr__())
		elif len(self.elif_conds) > 0:
			f.writenl('if(%s) ' % self.elif_conds[0].__repr__())
			f.write(self.elif_blocks[0].__repr__())
			for i, elif_cond in self.elif_conds:
				f.writenl('else if%s' % elif_cond.__repr__())
				f.write(self.elif_blocks[i].__repr__())
			if self.else_block is not None:
				f.writenl('else')
				f.write(self.else_block.__repr__())
		elif self.else_block is not None:
			f.write(self.else_block.__repr__())
		return s.getvalue()

class block_stmt(object):
	indent_level = 0
	def __init__(self, *args):
		self.stmts = [stmt for stmt in args]

	def append(self, stmt):
		self.stmts.append(stmt)
		return self

	def __repr__(self):
		rep = '%sbegin\n' % (block_stmt.indent_level * '\t')
		block_stmt.indent_level += 1
		for stmt in self.stmts:
			rep += '%s%s\n' % (block_stmt.indent_level * '\t', stmt.__repr__())
		block_stmt.indent_level -= 1
		rep += '%send\n' % (block_stmt.indent_level * '\t')
		return rep
