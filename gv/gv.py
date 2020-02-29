import os
import re
import sys
import argparse

from stream import stream

def tostr(v):
	if v is None: return ''
	return v

def replace_conditionals(lines):
	newlines = lines
	return newlines

def replace_assignments(lines):
	newlines = []
	found_module = False
	found_impl = False
	for i, line in enumerate(lines):
		if 'MODULE' in line:
			found_module = True
			found_impl = False
		elif 'class' in line:
			found_module = False
			found_impl = False

		if found_module and '__impl__' in line:
			found_impl = True

		if found_module and found_impl:
			match = re.match(r'(\t*)([a-zA-Z]+[a-zA-Z\d_]*\.)?([a-zA-Z]+[a-zA-Z\d_]*)(\[[\d:]+\])? *=([^=][^\n]*)\n', line)
			if match is not None:
				indent = match.group(1)
				classname = 'None'
				if match.group(2) is not None:
					classname = match.group(2).replace('.', '')
				name = tostr(match.group(3))
				pre_eq = '%s%s%s' % (
					tostr(match.group(2)), 
					tostr(match.group(3)), 
					tostr(match.group(4)))
				post_eq = '%s%s' % (tostr(match.group(4)), tostr(match.group(5)))

				if match.group(2) is None:
					newlines.append('%sif EXISTS("%s", locals(), globals()) and isinstance(%s, BIT):\n' % (
						indent, name, pre_eq))
					newlines.append('%s\tCONNECT(%s, (%s))\n' % (indent, pre_eq, post_eq))
					newlines.append('%selse:\n' % (indent))
					newlines.append('\t%s' % line)
				else:
					newlines.append('%sif EXISTS("%s", %s) and isinstance(%s, BIT):\n' % (
						indent, name, classname, pre_eq))
					newlines.append('%s\tCONNECT(%s, (%s))\n' % (indent, pre_eq, post_eq))
					newlines.append('%selse:\n' % (indent))
					newlines.append('\t%s' % line)
			else:
				newlines.append(line)
		else:
			newlines.append(line)
	return newlines

def main(args):
	f = stream(sys.stdout)
	if args.dest:
		if os.path.exists(os.path.dirname(args.dest)):
			f = stream(open(args.dest, 'w+'))
		else:
			print('Not found: %s' % args.dest)
			return

	if not os.path.exists(args.top[0]):
		print('Could not find top %s' % args.top)

	with open(args.top[0], 'r') as t:
		lines = t.readlines()
		lines.insert(0, 'from gv import COND, EXISTS, CONNECT\n')
		lines = replace_conditionals(lines)
		lines = replace_assignments(lines)

	for line in lines:
		f.write(line)
	f.blank()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--dest', 
		type=str, help='Destination')
	parser.add_argument('top', 
		nargs=1, help='top')
	args = parser.parse_args()
	main(args)
