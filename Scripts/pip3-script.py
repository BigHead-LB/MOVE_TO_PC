#!C:\Users\Administrator\PycharmProjects\python_packing_64bit\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'pip==24.3.1','console_scripts','pip3'
__requires__ = 'pip==24.3.1'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('pip==24.3.1', 'console_scripts', 'pip3')()
    )
