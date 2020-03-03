from io import StringIO
import stream
import elaborate
import bit

indent_level = 0
class stmt(object):
	def __init__(self, expr=None):
		self._gvie = expr
		elaborate.ELABORATE.stmt(self)

	def expr(self):
		return self._gvie

	def set_expr(self, expr):
		self._gvie = expr

	def __repr__(self):
		return '%s%s;\n' % (indent_level * '\t', self.expr().__repr__())

class cond_stmt(stmt):
	class metadata(object):
		def __init__(self):
			self.if_cond = None
			self.if_block = None
			self.elif_conds = []
			self.elif_blocks = []
			self.else_block = None

	def __init__(self):
		self._gvic = cond_stmt.metadata()
		super().__init__()

	def if_block(self):
		return self._gvic.if_cond, self._gvic.if_block

	def set_if_block(self, cond, block):
		self._gvic.if_cond = cond
		self._gvic.if_block = block

	def elif_blocks(self):
		return self._gvic.elif_conds, self._gvic.elif_blocks 

	def append_elif_block(self, cond, block):
		self._gvic.elif_conds.append(cond)
		self._gvic.elif_blocks.append(block)

	def set_if_block(self, cond, block):
		self._gvic.if_cond = cond
		self._gvic.if_block = block

	def else_block(self):
		return self._gvic.else_block 

	def set_else_block(self, block):
		self._gvic.else_block = block

	def __repr__(self):
		s = StringIO()
		f = stream.stream(s)
		if_cond, if_block = self.if_block()
		elif_conds, elif_blocks = self.elif_blocks()
		if if_cond is not None:
			f.writenl('%sif%s ' % (
				indent_level * '\t', if_cond.__repr__()))
			f.write(if_block.__repr__())
			for elif_cond, elif_block in zip(elif_conds, elif_blocks):
				f.writenl('%selse if%s' % (
					indent_level * '\t', elif_cond.__repr__()))
				f.write(elif_block.__repr__())
			if self.else_block() is not None:
				f.writenl('%selse' % (indent_level * '\t'))
				f.write(self.else_block().__repr__())
		elif len(elif_conds) > 0:
			f.writenl('%sif(%s) ' % (
				indent_level * '\t', elif_conds[0].__repr__()))
			f.write(elif_blocks[0].__repr__())
			for elif_cond, elif_block in zip(elif_conds[1:], elif_blocks[1:]):
				f.writenl('%selse if%s' % (
					indent_level * '\t', elif_cond.__repr__()))
				f.write(elif_block.__repr__())
			if self.else_block() is not None:
				f.writenl('%selse' % (indent_level * '\t'))
				f.write(self.else_block().__repr__())
		elif self.else_block() is not None:
			f.write(self.else_block().__repr__())
		return s.getvalue()

class inst_stmt(stmt):
	inst_count = 0
	class metadata(object):
		def __init__(self):
			self.module = None
			self.name = None
			self.cxns = []

	def __init__(self, module):
		self._gvii = inst_stmt.metadata()
		self._gvii.module = module
		self._gvii.name = 'inst%d' % inst_stmt.inst_count
		inst_stmt.inst_count += 1

	def name(self):
		return self._gvii.name

	def set_name(self, name):
		self._gvii.name = name

	def module(self):
		return self._gvii.module

	def set_module(self, module):
		self._gvii.module = module

	def cxns(self):
		return self._gvii.cxns

	def append_cxn(self, cxn):
		self._gvii.cxns.append(cxn)

	def connect(self, cxn):
		self.append_cxn(cxn)

	def __repr__(self):
		s = StringIO()
		f = stream.stream(s)
		f.write('%s %s(' % (self.module().name(), self.name()))
		more_than_one = False
		indented = False
		decls = self.module().decls()
		for k in decls:
			p = decls[k]
			if p.dxn() is not None:
				if more_than_one:
					f.writenl(',')
					if not indented:
						f.indent()
						indented = True
				f.write(p.__cxn_repr__())
				more_than_one = True

		f.unindent()
		f.writenl(');')

		return s.getvalue()

class block_stmt(stmt):
	def __init__(self, *args):
		self._gvibs = [stmt for stmt in args]

	def stmts(self):
		return self._gvibs

	def append_stmt(self, stmt):
		self._gvibs.append(stmt)
		return self

	def __repr__(self):
		global indent_level
		rep = '%sbegin\n' % (indent_level * '\t')
		indent_level += 1
		for stmt in self._gvibs:
			rep += '%s' % stmt.__repr__()
		indent_level -= 1
		rep += '%send\n' % (indent_level * '\t')
		return rep

def connect(dest, src):
	import expr
	return stmt(expr.assign_expr(dest, src))

class cond(object):
	def __init__(self, evaluated=None):
		self.evaluated = evaluated
		self.logic_conditional = False
		self.rep = cond_stmt()

	def IF(self, condition, body):
		expr = condition()
		if isinstance(expr, bit.bit):
			# Elaborate here
			elaborate.ELABORATE.block()
			body() 
			block = elaborate.ELABORATE.endblock()
			self.logic_conditional = True
			self.rep.set_if_block(expr, block)
			return self
		if expr:
			body()
			self.evaluated = True
			return self
		return self

	def ELIF(self, condition, body):
		if self.evaluated == True:
			return self
		expr = condition()
		if isinstance(expr, bit.bit) or self.logic_conditional:
			# Elaborate here
			elaborate.ELABORATE.block()
			body() 
			block = elaborate.ELABORATE.endblock()
			self.logic_conditional = True
			if type(expr) is bool:
				expr = bit.bit(1, int(expr))
			self.rep.append_elif_block(expr, block)
			return self
		if self.evaluated is None and expr:
			body()
			self.evaluated = True
			return self
		self.evaluated = False
		return self

	def ELSE(self, body):
		if self.evaluated == True:
			return self
		if self.logic_conditional or self.evaluated == False:
			elaborate.ELABORATE.block()
			body() 
			block = elaborate.ELABORATE.endblock()
			self.rep.set_else_block(block)
			self.evaluated = True
		return self
