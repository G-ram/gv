import sys

from gv import MODULE, STRUCT, UNION, BIT, REG, INPUT, OUTPUT
from gv import ELABORATE, stream

GLOBAL = 6

class block_t(UNION):
	def __init__(self, value=None):
		super().__init__(value)

	def impl(self):
		self.w = BIT(256)
		self.b = BIT(32)(8)

class test(MODULE):
	def impl(self):
		self.i = INPUT(block_t())
		self.o = INPUT(block_t())
		self.o = self.i | 0b1110

class top(MODULE):
	def __init__(self):
		super().__init__()

	def impl(self):
		self.a = INPUT(block_t())
		self.b = INPUT(BIT(32)(8))
		self.c = OUTPUT(BIT(4))
		self.c = self.a[0:1] & self.b[0:1]
		l = block_t()

		test_inst = test()
		test_inst.i = self.c
		l.w = test_inst.o

		test_inst2 = test()
		test_inst2.i = self.c
		l.w = test_inst2.o

		if self.c == BIT(2, 3):
			self.c = BIT(2, 1)
		elif self.c == BIT(2, 1):
			self.c = BIT(2, 0)

def main():
	a = top()
	ELABORATE.dump(stream(sys.stdout))

if __name__ == '__main__':
	main()