import winshell
from win32com.client import Dispatch

# get the path to the Start Menu folder
start_menu = winshell.startup()

# get the list of all programs installed on the system
programs = winshell.programs()

# create a Windows Shell object
shell = Dispatch('WScript.Shell')
print(programs)
# loop through each program and create a shortcut in the Start Menu folder
for program in programs:
    print(program)
    # shortcut = shell.CreateShortcut(f'{start_menu}\\{program}.lnk')
    # shortcut.TargetPath = program
    # shortcut.WorkingDirectory = program
    # shortcut.Save()