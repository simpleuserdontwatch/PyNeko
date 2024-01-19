"""
The converter of .ico to .png (Batch)
"""
import glob
import os
from PIL import Image

for i in glob.glob('*.ico'):
    a = Image.open(i)
    a.save(a.filename.split('.')[0]+".png")
    a.close()
    os.remove(i)
