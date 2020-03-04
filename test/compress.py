import sys
import argparse
from math import log2

from gv import MODULE, STRUCT, UNION, BIT, REG, INPUT, OUTPUT
from gv import ELABORATE, stream

class block_t(UNION):
	def __init__(self, z):
		self.z = z
		super().__init__()

	def impl(self):
		self.w = BIT(self.z)(32)
		self.b = BIT(self.z * 32)

class compress(MODULE):
	def __init__(self, g, z):
		self.g = g
		self.z = z
		self.p = 32
		super().__init__()

	def block_idx_t(self):
		return BIT(int(log2(self.z * self.p)))

	def block_status_t(self):
		return BIT(int(log2(self.z)))

	def msb_t(self):
		return BIT(int(log2(self.p)))

	def impl(self):
		self.c = INPUT(BIT(1))
		self.block = INPUT(block_t(self.z))
		self.cc = OUTPUT(BIT(1))
		self.cblock = OUTPUT(block_t(self.z))

		tblock = block_t(self.z)
		cblock = block_t(self.z)
		sblock = block_t(self.z)
		n = self.block_status_t()
		z = self.block_status_t()
		s = self.block_status_t()

		msb = self.msb_t()

		INTERLEAVE_COUNT = 32 // self.g
		for i in range(self.z):
			if((self.block.w[i][self.p - 1] == 1) & (~self.c)):
				tblock.w[i] = ~self.block.w[i]
				n[i] = 1
			for j in range(INTERLEAVE_COUNT):
				cblock_idx_low = j * self.z * self.g + i * self.g
				cblock_idx_high = cblock_idx_low + self.g - 1
				tblock_idx_low = i * 32 + j * self.g
				tblock_idx_high = tblock_idx_low + self.g - 1
				cblock.b[cblock_idx_low:cblock_idx_high] = tblock.b[tblock_idx_low:tblock_idx_high] 
	
		for i in range(self.z):
			z[i] = cblock.w[i] == BIT(self.p, 0)	
			s[i] = cblock.w[self.p - 1] & (~z[i])

		for i in range(self.z):
			if s[i] == 1:
				cblock.w[i] = ~self.block.w[i]

		tmp = BIT(self.p-1)
		for i in range(self.p-1, -1, -1):
			tmp[i] = cblock[i][0]
			for j in range(1, self.z):
				tmp[i] = tmp[i] | cblock[j][i]
			if (~msb).redor() & tmp[i]:
				msb = i + 1

		tblock = cblock
		cblock = 0
		cblock[0:self.z-1] = n
		cblock[self.z:2*self.z-1] = z
		cblock[2*self.z:3*self.z-1] = z
		msb_width = int(log2(self.p))
		cblock[3*self.z:3*self.z+msb_width-1] = msb

		diff = self.block_idx_t()
		shift = self.msb_t()
		diff = self.p - msb
		for i in range(self.z):
			if z[i] == 1:
				sblock.w[i] = 0
			else:
				sblock.w[i] = tblock.w[i]
			sblock = sblock << shift
			cblock.b |= sblock
			sblock = 0
			if i < self.z - 1:
				if z[i]:
					shift = shift + i 
				else:
					shift = shift + 32
					

def main(args):
	a = compress(args.g, args.z)
	ELABORATE.dump(stream(sys.stdout))

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-g', '--g', type=int, default=4, help='G')
	parser.add_argument('-z', '--z', type=int, default=8, help='Z')
	args = parser.parse_args()
	main(args)