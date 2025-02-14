import sys
import argparse
import textwrap
from pathlib import Path
from fontTools.ttLib import TTFont

try:
	from wcwidth import wcswidth
except:
	WCWITCH_NOT_FOUND = True
else:
	WCWITCH_NOT_FOUND = False

WINDOWS_ENGLISH_IDS = 3, 1, 1033
MAC_ROMAN_IDS = 1, 0, 0

NAME_ID = {
	'COPYRIGHT': 0,
	'FAMILY_NAME': 1,
	'STYLE': 2,
	'UNIQUE_ID': 3,
	'FULL_NAME': 4,
	'VERSION': 5,
	'POSTSCRIPT_NAME': 6,
	'TRADEMARK': 7,
	'MANUFACTURER': 8,
	'DESIGNER': 9,
	'DESCRIPTION': 10,
	'VENDOR_URL': 11,
	'DESIGNER_URL': 12,
	'LICENSE_DESCRIPTION': 13,
	'LICENSE_INFO_URL': 14,
	'PREFERRED_FAMILY_NAME': 16,
	'PREFERRED_STYLE': 17,
	'COMPATIBLE_FULL_NAME': 18,
	'SAMPLE_TEXT': 19,
	'PS_CID_FINDFONT_NAME': 20,
	'WWS_FAMILY_NAME': 21,
	'WWS_STYLE': 22
}

def resolve_label(nameID):
	LABELS = {
		0:  'Copyright',
		1:  'Family name',
		2:  'Style',
		3:  'Unique identifier',
		4:  'Full name',
		5:  'Version',
		6:  'PostScript name',
		7:  'Trademark',
		8:  'Manufacturer',
		9:  'Designer',
		10: 'Description',
		11: 'Vendor URL',
		12: 'Designer URL',
		13: 'License description',
		14: 'License info URL',
		16: 'Preferred family name',
		17: 'Preferred style',
		18: 'Compatible full name',
		19: 'Sample text',
		20: 'PS CID findfont name',
		21: 'WWS family name',
		22: 'WWS style'
	}

	try:
		return LABELS[nameID]
	except:
		return f'{nameID=}'

def validate_path(path):
	valid_path = Path(path).resolve()
	if not valid_path.exists():
		raise argparse.ArgumentTypeError(
			f"'{valid_path.name}' could not be found"
		)
	return valid_path

def length(text):
	if WCWITCH_NOT_FOUND:
		return len(text)
	total_width = 0
	for char in text:
		char_width = wcswidth(char)
		if char_width > 0:
			total_width += char_width
	return total_width

def format_string(text, max_width=49):
	if length(text) > max_width:
		string = ''
		current_width = 0
		for char in text:
			char_width = length(char)
			if current_width + char_width > max_width:
				return string
			else:
				string += char
				current_width += char_width
	else:
		return text

def wrap_text(text, max_width=74, indent_width=23):
	def wrap_line(line):
		lines = []
		current_line = ''
		current_width = 0
		indent = ' ' * indent_width

		for char in line:
			char_width = length(char)
			if current_width + char_width <= max_width:
				if current_line == '' and char == ' ':
					continue
				current_line += char
				current_width += char_width
			else:
				if char == ' ':
					lines.append(indent + current_line)
					current_line = ''
					current_width = 0
				else:
					last_space = current_line.rfind(' ', int(max_width * 0.5))
					if last_space == -1:
						lines.append(indent + current_line)
						current_line = char
						current_width = char_width
					else:
						lines.append(indent + current_line[:last_space])
						current_line = current_line[last_space + 1:] + char
						current_width = length(current_line)

		if current_line:
			lines.append(indent + current_line)
		return '\n'.join(lines)

	if length(text) > max_width:
		original_lines = text.splitlines()
		wrapped_text = '\n'.join(wrap_line(line) for line in original_lines)
		return wrapped_text.strip()
	else:
		return text

def show_raw(table, shorten_width=False):
	print('-------------------------------------------------------------------------------------------------')
	print('platformID  platEncID   langID      nameID      string')
	print('-------------------------------------------------------------------------------------------------')

	for r in table.names:
		if shorten_width:
			s = format_string(str(r))
		else:
			s = str(r).replace('\r', '\n')

		print(
			f'{r.platformID:<10}  '
			f'{r.platEncID:<10}  '
			f'{r.langID:<10}  '
			f'{r.nameID:<10}  '
			f'{s}'
		)

def show_friendly(table):
	PRIORITY_NAMES = [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 16, 17, 18]
	printed_names = set()

	for r in table.names:
		if r.langID == 1033 and r.nameID in PRIORITY_NAMES:
			printed_names.add(str(r))
			print(
				f'{resolve_label(r.nameID):<23}'
				f'{wrap_text(str(r))}'
			)
	for i in range(25):
		for r in table.names:
			if r.langID == 1033 and \
			   r.nameID not in PRIORITY_NAMES and \
			   r.nameID == i:
				if str(r) in printed_names:
					continue
				print(
					f'{resolve_label(r.nameID):<23}'
					f'{wrap_text(str(r))}'
				)
	for i in range(25):
		for r in table.names:
			if r.langID not in [0, 1033] and \
			   r.nameID in PRIORITY_NAMES and \
			   r.nameID == i:
				print(
					f'{resolve_label(r.nameID):<23}'
					f'{wrap_text(str(r))}'
				)
	for i in range(25):
		for r in table.names:
			if r.langID not in [0, 1033] and \
			   r.nameID not in PRIORITY_NAMES and \
			   r.nameID == i:
				print(
					f'{resolve_label(r.nameID):<23}'
					f'{wrap_text(str(r))}'
				)

def show(args):
	for count, path in enumerate(args.path):
		font = TTFont(path)
		table = font['name']
		if count > 0:
			print('\n')
		print(f"{Path(path).name}")
		show_raw(table, shorten_width=True)
		print()
		show_friendly(table)

def get_string(name_id, table):
	for plat_id, enc_id, lang_id in (WINDOWS_ENGLISH_IDS, MAC_ROMAN_IDS):
		record = table.getName(
			nameID=name_id,
			platformID=plat_id,
			platEncID=enc_id,
			langID=lang_id
		)
		if record:
			return str(record)
	return ''

def set_string(string, name_id, plat_id, enc_id, lang_id, table):
	table.setName(
		string,
		nameID=name_id,
		platformID=plat_id,
		platEncID=enc_id,
		langID=lang_id
	)

def set_string_in_record(string, record, table):
	table.setName(
		string,
		nameID=record.nameID,
		platformID=record.platformID,
		platEncID=record.platEncID,
		langID=record.langID
	)

def set_string_by_language(string, name_id, lang_id, table):
	for record in table.names:
		if record.nameID == name_id and record.langID == lang_id:
			set_string_in_record(string, record, table)

def replace_string(old_string, new_string, table):
	for record in table.names:
		string = str(record)
		string = string.replace(old_string, new_string)
		set_string_in_record(string, record, table)

def replace_postscript_name(args):
	path = args.path[0]
	font = TTFont(path)
	table = font['name']
	for record in table.names:
		if record.nameID == NAME_ID['POSTSCRIPT_NAME']:
			set_string_in_record(args.postscript_name, record, table)
	font.save(path)
	print(f"updated '{Path(path).name}'")

def replace(args):
	count = 0
	for path in args.path:
		font = TTFont(path)
		table = font['name']
		replace_string(args.old_string, args.new_string, table)
		font.save(path)
		print(f"updated '{Path(path).name}'")
		count += 1
	print(f"updated {count} font{'s' if count > 1 else ''}")

def modify(args):
	WIN_STYLES = [
		'Regular',
		'Regular Italic',
		'Regular Oblique',
		'Italic',
		'Bold',
		'Bold Italic',
		'Bold Oblique'
	]

	if args.win:
		USE_WIN_STYLES = True
	else:
		USE_WIN_STYLES = False

	count = 0

	for path in args.path:
		font = TTFont(path)
		table = font['name']

		if args.style:
			style = args.style
		else:
			style = get_string(NAME_ID['STYLE'], table)

		if not style:
			print(f"font style is empty.", file=sys.stderr)
			sys.exit(1)

		family_name = args.family_name
		preferred_family_name = family_name
		preferred_style = style

		if USE_WIN_STYLES and preferred_style not in WIN_STYLES:
			if 'Italic' in preferred_style:
				family_name = f"{family_name} {preferred_style.replace(' Italic', '')}"
				style = 'Italic' if 'Italic' in style else 'Regular'
			elif 'Oblique' in preferred_style:
				family_name = f"{family_name} {preferred_style.replace(' Oblique', '')}"
				style = 'Oblique' if 'Oblique' in style else 'Regular'

		full_name = f"{preferred_family_name} {preferred_style}"

		# without 'Regular' in the full name
		# full_name = preferred_family_name + \
		# 	('' if preferred_style == 'Regular' else f" {preferred_style.replace('Regular ', '')}")

		# no space on postscript name
		postscript_family_name = preferred_family_name.replace(' ', '')
		postscript_style = preferred_style.replace(' ', '')

		# without 'Regular' in the postscript name
		# postscript_style = \
		# 	'' if preferred_style == 'Regular' else f"{preferred_style.replace('Regular', '')}"
		# postscript_style = postscript_style.replace(' ', '')

		postscript_name = f"{postscript_family_name}-{postscript_style}"

		# store the orginal full font name and postscript name from the font
		original_full_name = get_string(NAME_ID['FULL_NAME'], table)
		original_postscript_name = get_string(NAME_ID['POSTSCRIPT_NAME'], table)

		# replace the original font name in unique ID with new font name
		original_unique_id = get_string(NAME_ID['UNIQUE_ID'], table)

		unique_id = ''
		if original_postscript_name in original_unique_id:
			unique_id = original_unique_id.replace(original_postscript_name, postscript_name)
		elif original_full_name in original_unique_id:
			unique_id = original_unique_id.replace(original_full_name, full_name)

		# update the OpenType table with new values
		for plat_id, enc_id, lang_id in [MAC_ROMAN_IDS, WINDOWS_ENGLISH_IDS]:
			set_string(family_name, NAME_ID['FAMILY_NAME'], plat_id, enc_id, lang_id, table)
			set_string(full_name, NAME_ID['FULL_NAME'], plat_id, enc_id, lang_id, table)
			set_string(postscript_name, NAME_ID['POSTSCRIPT_NAME'], plat_id, enc_id, lang_id, table)
			set_string(preferred_family_name, NAME_ID['PREFERRED_FAMILY_NAME'], plat_id, enc_id, lang_id, table)
			set_string(preferred_style, NAME_ID['PREFERRED_STYLE'], plat_id, enc_id, lang_id, table)
			if unique_id:
				set_string(unique_id, NAME_ID['UNIQUE_ID'], plat_id, enc_id, lang_id, table)
			if USE_WIN_STYLES:
				set_string(style, NAME_ID['STYLE'], plat_id, enc_id, lang_id, table)

		# CFF table naming for CFF fonts (only)
		if "CFF " in font:
			try:
				cff = font['CFF ']
				cff.cff[0].FamilyName = family_name
				cff.cff[0].FullName = full_name
				cff.cff.fontNames = [postscript_name]
			except Exception as e:
				print(f"unable to update CFF table with the new names.", file=sys.stderr)
				print(f"{e}", file=sys.stderr)

		# write changes to the font file
		font.save(path)
		print(f"updated '{Path(path).name}'")
		count += 1

	print(f"updated {count} font{'s' if count > 1 else ''}")

def main():
	parser = argparse.ArgumentParser(
		formatter_class=argparse.RawTextHelpFormatter,
		epilog=textwrap.dedent("""\
			additional information:
			  module 'wcwidth' is required to properly display text containing unicode characters""")
	)
	parser.add_argument(
		'-f',
		'--family-name',
		type=str,
		default='',
		help="new font family name"
	)
	parser.add_argument(
		'-s',
		'--style',
		type=str,
		default='',
		help="new style (subfamily)"
	)
	parser.add_argument(
		'-p',
		'--postscript-name',
		type=str,
		default='',
		help="new PostScript name"
	)
	parser.add_argument(
		'-w',
		'--win',
		action='store_true',
		help="for font style (subfamily) naming that is Windows compatible"
	)
	parser.add_argument(
		'-d',
		'--old-string',
		type=str,
		default='',
		help="string to be replaced"
	)
	parser.add_argument(
		'-n',
		'--new-string',
		type=str,
		default='',
		help="new string"
	)
	parser.add_argument(
		'path',
		metavar='FONT',
		type=validate_path,
		nargs='+',
		help="path to a font, or multiple fonts"
	)
	args = parser.parse_args()

	if args.family_name:
		modify(args)
	elif args.old_string and args.new_string:
		replace(args)
	elif args.postscript_name:
		replace_postscript_name(args)
	else:
		show(args)

if __name__ == '__main__':
	main()
