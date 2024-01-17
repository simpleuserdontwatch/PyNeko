from PIL import Image
import glob
import os

for i in glob.glob('*.ico'):
    a = Image.open(i)

    a.save(a.filename.split('.')[0]+".png")

    a.close()
    
    os.remove(i)
