#############################################
# This is the set up script in order to     #
# compile this python program to executable #
# with py2exe.                              #   
# Updated June 2021                         #
# By zxzq(https://zxzq.me)                  #
# See my github for detail of this program  #
# https://github.com/bllovetx/myCGprogram   #
#                                           #
# usage:python setup.py py2exe              #
#############################################

from distutils.core import setup
import py2exe
from glob import glob
import platform
import os

myDataFiles = [
    ('platforms', glob(r'C:\Users\ASUS\anaconda3\Library\plugins\platforms\qwindows.dll')),
    ('imageformats', glob(r'C:\Users\ASUS\anaconda3\Library\plugins\imageformats\qgif.dll')),
    ('imageformats', glob(r'C:\Users\ASUS\anaconda3\Library\plugins\imageformats\qicns.dll')),
    ('imageformats', glob(r'C:\Users\ASUS\anaconda3\Library\plugins\imageformats\qico.dll')),
    ('imageformats', glob(r'C:\Users\ASUS\anaconda3\Library\plugins\imageformats\qjpeg.dll')),
    ('imageformats', glob(r'C:\Users\ASUS\anaconda3\Library\plugins\imageformats\qsvg.dll')),
    ('imageformats', glob(r'C:\Users\ASUS\anaconda3\Library\plugins\imageformats\qtga.dll')),
    ('imageformats', glob(r'C:\Users\ASUS\anaconda3\Library\plugins\imageformats\qtiff.dll')),
    ('imageformats', glob(r'C:\Users\ASUS\anaconda3\Library\plugins\imageformats\qwbmp.dll')),
    ('imageformats', glob(r'C:\Users\ASUS\anaconda3\Library\plugins\imageformats\qwebp.dll')),
]

# copy pictures
for files in os.listdir('./pics/'):
    f1 = './pics/' + files
    if os.path.isfile(f1): # skip directories
        f2 = ('pics', [f1])
        myDataFiles.append(f2)


#print(myDataFiles)
setup(
    windows=[{
        "script": 'cg_gui.py',
        "icon_resources": [(0, "pics/favicon.ico")],
        "dest_base": "MyCGProgram"
    }],
    options={
        "py2exe":{
            "includes":["sip"]#,
            #'bundle_files': 0 # not working
        }
    },
    data_files=myDataFiles
)