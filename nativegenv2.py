import re
import os 
import time
from datetime import datetime

system = {}
app = {}
audio = {}


def get_native_hashes(src: str) -> list:
    match = re.search(r"(?<=\/\/\s)(0x[A-Za-z0-9]+)", src)
    if(match != None):
        return match
    else:
        pass

def get_namespace(src: str) -> str:
    match = re.search(r"namespace (\w+)", src)
    if(match != None):
        return match 
    else: 
        pass

with open("natives.hpp") as n:
    for line in n:
        namespace = get_namespace(line)
        hashes = get_native_hashes(line)
        if(hashes):
            print(hashes.group())
        if(namespace):
            print("Current Namespace: {}".format(namespace.group()))