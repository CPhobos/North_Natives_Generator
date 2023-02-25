import re
import os 
from time import time
from datetime import datetime

py_keywords = ["from", "property", "hash", "object", "range"]
arg_pattern = re.compile("float\*?|int\*?|Any\*?|Object\*?|unsigned\*?|BOOL\*?|const char\\*|char\\*")
pointer_pattern = re.compile("int\\*|float\\*|Any\\*|Vector3\\*|BOOL\\*|unsigned\\*")

native_types = {
    "unsigned": "Int",
    "Hash": "Int",
    "char": "Str",
    "Any": "placeholder",
    "float": "Float",
    "int": "Int",
    "BOOL": "Bool",
    "Vector3": "Vec3",
    "Vector2": "Vec2",
    "Object": "Int",
    "const": "Str"
}


def remove_py_keywords(arg: str) -> str:
	for keyword in py_keywords:
		if(re.search(keyword, arg)):
			return re.sub(keyword, "_{}".format(keyword), arg)
	return arg

def get_formatted_args(input_args: str) -> str:
    if(input_args != None):
        return remove_py_keywords(re.sub(arg_pattern,  "", input_args))

def get_native_hashes(src: str) -> list:
    return re.search(r"(?<=\/\/\s)(0x[A-Za-z0-9]+)", src)

def get_namespace(src: str) -> str:
    return re.search(r"(?<=namespace\s)(\w+)", src)

def get_native_name(src: str, native_format: str) -> str: 
    match = re.search(r"(\w+)\s*\(", src)
    if(match):
        if(native_format == "fivem"):
            return fivem_format(match.group(1))
        elif(native_format == "snake_lower"):
            return match.group(1).lower()
        return match.group(1).lower()

def get_native_args(src: str) -> str:
    match = re.search(r"\w+\((.*?)\)", src)
    if(match):
        return match.group(1)

def does_native_have_pointers(native_args: str) -> bool:
    if(native_args != None):
        return len(re.findall(pointer_pattern, native_args)) != 0


def extract_non_pointer_args(string: str) -> list:
    try:
        result = re.findall(r'(?<=int) (\w+)', string)[0]
    except:
        return ""
    return result

def get_pointer_count(arg) -> int:
	return len(re.findall("(\w+\*)", arg))

def format_pointer_result(native_args: int, pointer_type: str) -> str:
    if(native_args != None):
	    return "(" + ", ".join("result.raw[{}]{}".format(i, pointer_type) for i in range(1, get_pointer_count(native_args) + 1)) + ")"

def handle_pointers(native_src: list) -> str:
    arr = list(range(get_pointer_count(native_src)))
    for x in range(len(arr)):
        arr[x] = x + 1
    return ", ".join(str(n) for n in arr)

def get_native_result_type(native_src: str) -> str:
    if(native_src != None):
        match = re.search(r"static (\w+)", native_src)
        if(match):
            return match.group(1)

def find_natives_file() -> str:
	files = [f for f in os.listdir('.') if os.path.isfile(f)]
	for f in files:
		match = re.search("\w+\\.hpp|\w+\\.h", f)
		if(match != None):
			return match[0]
	return False

def has_args(src: str, include_comma: bool)-> str:
    if include_comma:
        return "," + src if src else ""
    return src if src else ""

def capitalize_after_underscore(s):
	split_str = s.split('_')
	split_str = [word.capitalize() for word in split_str]
	return '_'.join(split_str)

def fivem_format(strr):
	return re.sub("\_", "", capitalize_after_underscore(strr.lower()))

def sanitize_user_input(user_inp) -> str:
	if(len(re.findall("[a-zA-Z]", user_inp)) != 0):
		print("String found... Defaulting to fivem format..")
		return "fivem"
	if(user_inp == ""):
		print("No input received... Defaulting to fivem format..") 
		return "fivem"
	user_inp = int(user_inp)
	if(user_inp <= 3):
		if(user_inp == 1):
			return "snake_lower"
		elif(user_inp == 2):
			return "snake_cap"
		else:
			return "fivem"


user_input = input("""Which format do you wanna use? \n [1] Snake Case Lower \n [2] Snake Case Higher \n [3] Fivem \n""")
chosen_format = sanitize_user_input(user_input)

native_format = """
def {}({}):
	{} native.invoke({}{}){}
"""

namespace_format = """

{}["{}"] = {}

"""

pointer_template = """ 
def {}({}):
	native.output_flag({}, [{}])
	result = native.invoke({}, {})
	return {}
"""


native_file = open('native.py', "w")

native_file.write("""class dot_notation(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    """ + "\n")


natives_file = find_natives_file()
if(not natives_file):
	print("Natives file not found!")
	exit()

start_time = time()
with open(natives_file) as n:
    for line in n:
        namespace = get_namespace(line)
        cur_name = get_native_name(line, chosen_format) if get_native_name(line, chosen_format) else None
        cur_hash = get_native_hashes(line).group() if get_native_hashes(line) else None
        cur_args = get_native_args(line) if get_native_args(line) else None
        formatted_args = get_formatted_args(cur_args)
        return_type = get_native_result_type(line)
        if(return_type == "void" or return_type == None):
            return_type = ""
            returns = ""
        else:
            return_type = f".{native_types[return_type]}"
            returns = "return"
        pointer_result = format_pointer_result(cur_args, return_type)
        if(namespace):
            cur_namespace = namespace.group().lower()
            native_file.write(f"\n{cur_namespace} = {{}} \n")
            native_file.write(f"{cur_namespace} = dot_notation({cur_namespace})\n")
        if(cur_name):
            if(does_native_have_pointers(cur_args)):
                native_file.write(pointer_template.format(cur_name, extract_non_pointer_args(cur_args), cur_hash, handle_pointers(cur_args), cur_hash, extract_non_pointer_args(cur_args), pointer_result))
                native_file.write(namespace_format.format(cur_namespace, cur_name, cur_name).replace("\n", ""))
                native_file.write("\n")
            else:
                native_file.write(native_format.format(cur_name, has_args(formatted_args, False), returns, cur_hash, has_args(formatted_args, True), return_type))
                native_file.write(namespace_format.format(cur_namespace, cur_name, cur_name).replace("\n", ""))
                native_file.write("\n")
native_file.close()
end_time = time()
print("Done! Generated native.py in {:.2f} seconds".format(end_time - start_time))