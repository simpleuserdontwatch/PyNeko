from PIL import Image,ImageColor
import numpy as np

filename = "../nekoimages/still.png"

orig_color = (255,255,255,255)
replacement_color = ImageColor.getrgb("#9b9b9b")+(255,)
img = Image.open(filename).convert('RGBA')
data = np.array(img)
data[(data == orig_color).all(axis = -1)] = replacement_color
img2 = Image.fromarray(data, mode='RGBA')
img2.show()
