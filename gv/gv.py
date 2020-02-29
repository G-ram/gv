import sys
import argparse

from stream import stream

def main(args):
	f = stream(sys.stdout)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--dest', 
		type=str, help='Destination')
	parser.add_argument('top', 
		nargs=1, help='top')
	args = parser.parse_args()
	main(args)
