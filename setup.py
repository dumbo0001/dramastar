import sys
from cx_Freeze import setup, Executable

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"
    
# Dependencies are automatically detected, but it might need fine tuning.
includefiles = [ 'web\\templates', 'web\\static', 'core.ini', 'web.ini' ]

build_exe_options = { 
    'packages' : ['sqlalchemy.dialects.sqlite'],
    'namespace_packages' : ['repoze.lru'],
    'include_files' : includefiles,
}

executables = [
    Executable('dramastar.py', base = base)
]

setup(name='dramastar',
      version='0.1',
      description='Dramastar drama snatch & download',
      options = { 'build_exe' : build_exe_options },
      executables = executables
      )