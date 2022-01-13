import os, sys

from cx_Freeze import setup, Executable

arg = sys.argv
print(arg)

if arg[1].lower().startswith('bdist_msi'):
    MSI_build = True
elif arg[1].lower().startswith('build'):
    MSI_build = False
else:
    MSI_build = False

file_name = 'ScrMulti.scr'
program_name = 'ScreenMultimedia'

shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "DTI Playlist",           # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]playlist.exe",# Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     )
    ]

msi_data = {"Shortcut": shortcut_table}
bdist_msi_options = {'data': msi_data}


executables = [Executable("Main.py",
                          icon='Camera.ico',
                          targetName=file_name,
                          base="Win32GUI",
                          copyright="Shestakov Anton",
                          shortcutName=program_name,
                          shortcutDir='DesktopFolder'
                          )
               ]

excludes = ['asyncio', 'unittest', 'html', 'http', 'xmlrpc', 'PyQt5', 'test', 'distutils', 'pydoc_data', 'setuptools',
            'multiprocessing', 'lib2to3', 'concurrent', 'pyrect', 'pygetwindow', 'pyperclip', 'pytweening', 'pymsgbox',
            'curses', '_bz2', '_decimal', '_elementtree', '_hashlib', '_lzma', '_queue', '_ssl']

zip_include_packages = ['xml', 'urllib', 'pytz', 'pyscreeze', 'pyautogui', 'pkg_resources', 'PIL',
                        'mouseinfo', 'logging', 'json', 'importlib', 'exifread', 'encodings', 'email', 'ctypes',
                        'collections', 'mypack', 'tkinter', 'Tkinter']

include_files = []

if MSI_build:
    options = {
        'build_exe': {
            'include_msvcr': True,
            'include_files': include_files,
            'excludes': excludes,
            'zip_include_packages': zip_include_packages
        }
    }
else:
    options = {
        'build_exe': {
            'include_msvcr': True,
            'excludes': excludes,
            'zip_include_packages': zip_include_packages,
            'build_exe': program_name
        }
        # ,"bdist_msi": bdist_msi_options
    }

current_dir = os.getcwd()
print("Текущая директория:", current_dir)

if MSI_build:
    if not os.path.exists(f'{os.getcwd()}\\build\\exe.win32-3.8'):
        os.makedirs(f'{os.getcwd()}\\build\\exe.win32-3.8')
    os.chdir(f'{os.getcwd()}\\build\\exe.win32-3.8')
else:
    if not os.path.exists(f'{os.getcwd()}\\{program_name}'):
        os.makedirs(f'{os.getcwd()}\\{program_name}')
    os.chdir(f'{os.getcwd()}\\{program_name}')

file_bat = open('setup.bat', 'w')
file_bat.writelines('@echo off\n')
file_bat.writelines('setlocal\n')
file_bat.writelines(f'reg add "hkcu\control panel\desktop" /v SCRNSAVE.EXE /t reg_sz /d %cd%\\{file_name} /f\n')
file_bat.writelines(f'start %windir%\\System32\\rundll32.exe shell32.dll,Control_RunDLL desk.cpl,,1\n')
file_bat.writelines(f'start %cd%\\{file_name} /c\n')
file_bat.close()

os.chdir(current_dir)

setup(
    name=program_name,
    version="0.1",
    author="Shestakov Anton",
    description=program_name,
    executables=executables,
    options=options
)


if MSI_build:
    import shutil
    print("removing 'build\\'")
    shutil.rmtree(f'{os.getcwd()}\\build')
# os.removedirs(f'{os.getcwd()}\\build\\exe.win32-3.8')
# os.removedirs(f'{os.getcwd()}\\build\\bdist.win32')

# os.rename("Tkinter", "tkinter")

# cx_Freeze:
# setup.py build
# setup.py bdist_msi
