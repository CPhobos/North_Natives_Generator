import re
import os 
import time
from datetime import datetime

py_keywords = ["from", "property", "hash", "object", "range"]
arg_pattern = re.compile("float\*?|int\*?|Any\*?|Object\*?|unsigned\*?|BOOL\*?|const char\\*|char\\*")
pointer_pattern = re.compile("int\\*|float\\*|Any\\*|Vector3\\*|BOOL\\*|unsigned\\*")

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

def get_native_name(src: str) -> str: 
    return re.search(r"(\w+)\s*\(", src)

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
	    return "(" + ", ".join("result.raw[{}].{}".format(i, pointer_type) for i in range(1, get_pointer_count(native_args) + 1)) + ")"

def handle_pointers(native_src: list) -> str:
    arr = list(range(get_pointer_count(native_src)))
    for x in range(len(arr)):
        arr[x] = x + 1
    return ", ".join(str(n) for n in arr)

def get_native_result_type(native_src: str) -> str:
    if(native_src != None):
        match = re.search(r"\b(\w+)\*", native_src)
        if(match):
            return match.group(1)


native_format = """
def {}({}):
	{} print({}{})
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

def has_args(src: str, include_comma: bool)-> str:
    if include_comma:
        return "," + src if src else ""
    return src if src else ""

start_time = time.time()
with open("natives.hpp") as n:
    for line in n:
        namespace = get_namespace(line)
        cur_name = get_native_name(line).group(1).lower() if get_native_name(line) else None
        cur_hash = get_native_hashes(line).group() if get_native_hashes(line) else None
        cur_args = get_native_args(line) if get_native_args(line) else None
        formatted_args = get_formatted_args(cur_args)
        pointer_result = format_pointer_result(cur_args, get_native_result_type(cur_args))
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
                native_file.write(native_format.format(cur_name, has_args(formatted_args, False), "", cur_hash, has_args(formatted_args, True)))
                native_file.write(namespace_format.format(cur_namespace, cur_name, cur_name).replace("\n", ""))
                native_file.write("\n")
native_file.close()
end_time = time.time()
print("Done! Generated native.py in {:.2f} seconds".format(end_time - start_time))