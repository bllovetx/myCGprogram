# -*- mode: python ; coding: utf-8 -*-

#############################################
# This is the set up script in order to     #
# compile this python program to executable #
# with pyinstaller.                         #   
# Updated June 2021                         #
# By zxzq(https://zxzq.me)                  #
# See my github for detail of this program  #
# https://github.com/bllovetx/myCGprogram   #
#                                           #
# usage:pyinstaller cg_gui.spec             #
#############################################
import os

block_cipher = None

myDataFiles = [('favicon.ico', '.')]

version = '1.0.1'
programName = 'MyCGProgram'
myName = programName + '-ver' + version

# copy pictures
for files in os.listdir('./pics/'):
    f1 = './pics/' + files
    if os.path.isfile(f1): # skip directories
        f2 = (f1, 'pics')
        myDataFiles.append(f2)

a = Analysis(['cg_gui.py'],
             pathex=['D:\\NJU\\cs\\CG2021spring\\myCGprogram\\source'],
             binaries=[],
             datas=myDataFiles,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name=myName,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='favicon.ico' )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name=myName)
