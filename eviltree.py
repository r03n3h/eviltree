#!/bin/python3
#
# Written by Panagiotis Chartas (t3l3machus)

import os, re, argparse
from sys import exit

''' Colors '''
LINK = '\033[1;38;5;37m'
BROKEN = '\033[48;5;234m\033[1;31m'
DEBUG = '\033[0;38;5;214m'
GREEN = '\033[38;5;47m'
DIR = '\033[1;38;5;12m'
MATCH = '\033[1;38;5;201m' #220
RED = '\033[1;31m'
END = '\033[0m'


# -------------- Arguments & Usage -------------- #
parser = argparse.ArgumentParser()

parser.add_argument("-r", "--root-path", action="store", help = "The root path to walk.", required = True)
parser.add_argument("-o", "--only-interesting", action="store_true", help = "List only those files that their content includes interesting keywords.")
parser.add_argument("-k", "--keywords", action="store", help = "Comma separated keywords to search for in files.")
parser.add_argument("-a", "--match-all", action="store_true", help = "By default, files are marked when at least one keyword is matched. Use this option to mark only files that match all given keywords.")
parser.add_argument("-L", "--level", action="store", help = "Descend only level directories deep.", type = int)
parser.add_argument("-i", "--ignore-case", action="store_true", help = "Enables case insensitive keyword search ** for non-binary files only **.")
parser.add_argument("-v", "--verbose", action="store_true", help = "Print information about which keyword(s) matched.")
parser.add_argument("-f", "--full-pathnames", action="store_true", help = "Print absolute file and directory paths.")
parser.add_argument("-n", "--non-ascii", action="store_true", help = "Draw the directories tree using utf-8 characters (use this in case of \"UnicodeEncodeError: 'ascii' codec...\" along with -q).")
parser.add_argument("-d", "--directories-only", action="store_true", help = "List directories only.")
parser.add_argument("-l", "--follow-links", action="store_true", help = "Follows symbolic links if they point to directories, as if they were directories. Symbolic links that will result in recursion are avoided when detected.")
parser.add_argument("-q", "--quiet", action="store_true", help = "Do not print the banner on startup.")

args = parser.parse_args()


def exit_with_msg(msg):
	print(f'[{DEBUG}Debug{END}] {msg}')
	exit(1)
	

# Init keywords list
default_keywords = ['passw', 'admin', 'token', 'user', 'secret', 'login']
keywords = []

if not args.keywords:
	keywords = default_keywords

elif args.keywords:
	for word in args.keywords.split(","):
		if len(word.strip()) > 0:
			keywords.append(word.strip()) 
			
	if not len(keywords):
		keywords = default_keywords

total_keywords = len(keywords)


# Define depth level
if isinstance(args.level, int):
	depth_level = args.level if (args.level > 0) else exit_with_msg('Level (-l) must be greater than 0.') 

else:
	depth_level = 4096


# -------------- Functions -------------- #

def print_banner():

	padding = '  '

	E = [[' ', '┌', '─', '┐'], [' ', '├┤',' '], [' ', '└','─','┘']]
	V = [[' ', '┬', ' ', ' ', '┬'], [' ', '└','┐','┌', '┘'], [' ', ' ','└','┘', ' ']]
	I =	[[' ', '┬'], [' ', '│',], [' ', '┴']]
	L = [[' ', '┬',' ',' '], [' ', '│',' ', ' '], [' ', '┴','─','┘']]
	T = [[' ', '┌','┬','┐'], [' ', ' ','│',' '], [' ', ' ','┴',' ']]
	R = [[' ', '┬','─','┐'], [' ', '├','┬','┘'], [' ', '┴','└','─']]

	banner = [E,V,I,L,T,R,E,E]
	final = []
	print('\r')
	init_color = 43
	txt_color = init_color
	cl = 0

	for charset in range(0, 3):
		for pos in range(0, len(banner)):
			for i in range(0, len(banner[pos][charset])):
				clr = f'\033[38;5;{txt_color}m'
				char = f'{clr}{banner[pos][charset][i]}'
				final.append(char)
				cl += 1
				txt_color = txt_color + 36 if cl <= 3 else txt_color

			cl = 0

			txt_color = init_color
		init_color += 31

		if charset < 2: final.append('\n   ')

	print(f"   {''.join(final)}")
	print(f'{END}{padding}                   by t3l3machus\n')



def chill():
	pass


# regex = '[\s\S]{0,3}' + r + '[\s\S]{0,3}'		
# re.search(regex, open('/opt/testlink.txt').read(), re.I)

# ~ class SearchEngine:
	
	# ~ def __init__(self, mode):
		# ~ self.mode = mode
		
	
def file_inspector(file_path, mode = 0):
	
	# Regular mode, search binary and non-binary, case insensitive for non-binary files
	if mode == 0:	
				
		try:
			_file = open(file_path, 'r')
			content = _file.read()
			binary = False
		
		except UnicodeDecodeError:
			_file = open(file_path, 'rb')
			content = _file.read()		
			binary = True
	
		matched = []
			
		for w in keywords:
			w = re.escape(w)
			#w = '[\s\S]{0,3}' + w + '[\s\S]{0,3}'
			regex = re.compile(bytes(w.encode('utf-8'))) if binary else w
			
			if binary:
				found = re.search(regex, content)
			else:
				found = re.search(regex, content, re.I) if args.ignore_case else re.search(regex, content)
			
			if found:
				matched.append(w)
				
				if not args.match_all and not args.verbose:
					return MATCH

		if not args.match_all and len(matched):
			return [MATCH, f" {GREEN}[{', '.join(matched)}]{END}"]
		
		if args.match_all and len(matched) == total_keywords:
			return MATCH if not args.verbose else [MATCH, f" {GREEN}[{', '.join(keywords)}]{END}"]
			
		return ''
		
#	except UnicodeDecodeError:
#		return RED	



def fake2realpath(root_dir, target):
	
	back_count = target.count(".." + os.sep)
	
	if (re.search("\.\." + os.sep, target)) and (back_count == (root_dir.count(os.sep) - 1)):
		dirlist = [d for d in root_dir.split(os.sep) if d.strip()]
		dirlist.insert(0, os.sep)
		
		try:
			realpath = ''
			
			for i in range(0, back_count - 1):
				realpath += dirlist[i]
			
			realpath += target.split(".." + os.sep)[-1]
			return realpath
			
		except:
			return None
	
	elif not re.search(os.sep, target):
		return root_dir + target
	
	else:
		return target



child = '├── ' if not args.non_ascii else '|-- '
child_last = '└── ' if not args.non_ascii else '|-- '
parent = '│   ' if not args.non_ascii else '|   '
total_dirs_processed = 0
total_files_processed = 0


def eviltree(root_dir, intent = 0, depth = '', depth_level = depth_level):

	# ~ try:
	root_dirs = next(os.walk(root_dir))[1]
	root_files = next(os.walk(root_dir))[2]
	total_dirs = len(root_dirs)
	total_files = len(root_files)
	symlinks = []
	recursive = []
	global total_dirs_processed, total_files_processed
	# ~ total_dirs_processed += 1
	


	# Handle symlinks
	for d in root_dirs:
		if os.path.islink(f'{root_dir}{d}'):
			symlinks.append(d)
	
	
	# Process files
	root_files.sort()
	
	if not args.directories_only:
		
		for i in range(0, total_files):
			total_files_processed += 1
			file_path = f'{root_dir}{root_files[i]}'
			is_link = True if os.path.islink(file_path) else False
			target = os.readlink(file_path) if is_link else None

			# Verify target path if file is a symlink 
			if target:
				#target = (root_dir[0:-1] + target) if (re.search("\.\." + os.sep, target)) and (target.count(".." + os.sep) == (root_dir.count(os.sep) - 1)) else target # for symlink targets that include ../ in their path
				target = fake2realpath(root_dir, target) #if (re.search("\.\." + os.sep, target)) else target # for symlink targets that include ../ in their path
				is_dir = True if os.path.isdir(str(target)) else False
				is_broken = True if (not os.path.exists(str(target)) or is_dir) else False
				
			else:
				is_broken = None


			# Submit file for content inspection if it's not a broken symlink
			if (not is_link) or (is_link and not is_broken):
				details = file_inspector(file_path) if not is_link else file_inspector(target)
				
				if isinstance(details, list):
					color, verbose = details[0], details[1]
				else:
					color, verbose = details, ''
			
			else:
				color, verbose = '', ''
				
			
			# Color mark file accordingly in relation to the content inspection results
			if is_link:				
				linkcolor = BROKEN if is_broken else LINK
				filename = f'{linkcolor}{root_files[i]}{END} -> {color}{target}' if not args.full_pathnames else f'{linkcolor}{root_dir}{root_files[i]}{END} -> {color}{target}'
				
			else:
				filename = f'{color}{root_files[i]}' if not args.full_pathnames else f'{color}{root_dir}{root_files[i]}'
			
			# Print file branch
			if not args.only_interesting:
				print(f'{depth}{child}{color}{filename}{END}{verbose}') if (i < (total_files + total_dirs) - 1) else print(f'{depth}{child_last}{color}{filename}{END}{verbose}')
				
			elif args.only_interesting and (color and color != RED):
				print(f'{depth}{child}{color}{filename}{END}{verbose}') if (i < (total_files + total_dirs) - 1) else print(f'{depth}{child_last}{color}{filename}{END}{verbose}')


	# Process dirs
	root_dirs.sort()
	
	for i in range(0, total_dirs):
		total_dirs_processed += 1
		joined_path = root_dir + root_dirs[i]
		is_recursive = False
		directory = root_dirs[i] if not args.full_pathnames else (joined_path + os.sep)
		
		# Check if symlink and if target leads to recursion 
		if root_dirs[i] in symlinks:
			target = os.readlink(joined_path)
			#target = (root_dir + target) if (re.search("\.\." + os.sep, target)) and (target.count(".." + os.sep) == (root_dir.count(os.sep) - 1)) else target # for symlink targets that include ../ in their path
			target = fake2realpath(root_dir, target) #if (re.search("\.\." + os.sep, target)) else target # for symlink targets that include ../ in their path			
			is_recursive = ' [recursive, not followed]' if target == root_dir[0:-1] else ''
			
			if len(is_recursive):
				recursive.append(joined_path)
				
			print(f'{depth}{child}{LINK}{directory}{END} -> {DIR}{target}{END}{is_recursive}') if i < total_dirs - 1 else print(f'{depth}{child_last}{LINK}{directory}{END} -> {DIR}{target}{END}{is_recursive}')
			
		else:
			print(f'{depth}{child}{DIR}{directory}{END}') if i < total_dirs - 1 else print(f'{depth}{child_last}{DIR}{directory}{END}')
		
		sub_dirs = next(os.walk(joined_path))[1]
		sub_files = next(os.walk(joined_path))[2]
		
		if (not args.follow_links and root_dirs[i] not in symlinks) or (args.follow_links and not is_recursive):
			if (len(sub_dirs) or len(sub_files)) and (intent + 1) < depth_level:
				tmp = depth
				depth = depth + parent if i < (total_dirs - 1) else depth + '    '
				eviltree(joined_path + os.sep, intent + 1, depth)
				depth = tmp
			

	# ~ except Exception as e:
		# ~ exit_with_msg(f'Something went wrong: {e}')



def main():
		
	print_banner() if not args.quiet else chill()
	root_dir = args.root_path if args.root_path[-1] == os.sep else args.root_path + os.sep	
	
	if os.path.exists(root_dir):
		print(f'\r{DIR}{root_dir}{END}')
		eviltree(root_dir)
		print(f'\n{total_dirs_processed} directories, {total_files_processed} files')
		
	else:
		exit_with_msg('Directory does not exist.')
		
	print('\r')



if __name__ == '__main__':
	main()