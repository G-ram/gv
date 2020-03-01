import os
import re
import sys
import argparse

from stream import stream

def tostr(v):
	if v is None: return ''
	return v

def process_conditional_body(lines, branch, cond=None):
	return []

def find_conditional(lines, indent_level):
	for i, line in enumerate(lines):
		match = re.match(r'(\t*)(if([^:]+))|(elif([^:]+))|(else):\s*\n', line)
		branch = 2 # Else
		cond = None
		if match.group(2) is not None:
			branch = 0 # If
			cond = match.group(3)
		elif match.group(4) is not None:
			branch = 1 # Elif
			cond = match.group(5)
		if cond_match is not None and match.group(1).count('\t') == indent_level:
			for j, l in enumerate(lines[i+1:]):
				elif_else_match = re.match(r'(\t*)(elif([^:]+):)|(else:)\n', l)
				if elif_else_match is not None and \
					elif_else_match.group(1).count('\t') == indent_level:
					return process_conditional_body(lines[i+1:i+j], branch, cond)
	return process_conditional_body(lines)

def replace_conditionals(lines):
	newlines = []
	found_module = False
	found_impl = False
	indent_level = 0
	i = 0
	while i < len(lines):
		if 'MODULE' in lines[i]:
			found_module = True
			found_impl = False
		elif 'class' in lines[i]:
			found_module = False
			found_impl = False

		if found_module and '__impl__' in lines[i]:
			indent_level = lines[i].count('\t')
			found_impl = True

		if found_module and found_impl:
			newlines.append(lines[i])
			for j, l in enumerate(lines[i+1:]):
				match = re.match(r'\s*\n\s*', l)
				if match is not None:
					continue
				if l.count('\t') <= indent_level:
					break
			found_module = False
			found_impl = False
			newlines += find_conditional(lines[i+1:i + j])
			i += j
		else:
			newlines.append(lines[i])
			i += 1

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
