import sys

from gv import MODULE, STRUCT, UNION, BIT, REG, INPUT, OUTPUT, CONCAT
from gv import ELABORATE, stream

GLOBAL = 6

class block_t(UNION):
	def __init__(self, value=None):
		super().__init__(value)

	def __impl__(self):
		self.w = BIT(256)
		self.b = BIT(32)(8)

class TOP(MODULE):
	def __init__(self):
		super().__init__()

	def __impl__(self):
		self.a = INPUT(block_t())
		self.b = INPUT(BIT(32))
		self.c = OUTPUT(BIT(4))
		self.c = self.a[0:1] & self.b[0:1]
		l = 5

		if self.c == BIT(2, 3):
			self.c = BIT(2, 1)
		elif self.c == BIT(2, 1):
			self.c = BIT(2, 0)

def main():
	a = TOP()
	ELABORATE.dump(stream(sys.stdout))

if __name__ == '__main__':
	main()