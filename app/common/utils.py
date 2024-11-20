import re

ValidUsername = re.compile(r'^[a-zA-Z0-9_]{4,20}$')
ValidPassword = re.compile(r'^[a-zA-Z0-9!@$_?.]{8,}$')