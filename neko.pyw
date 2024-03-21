from tkinter import *
from PIL import Image, ImageTk, ImageColor, ImageFilter
import glob
import logging
import random
import numpy as np
import traceback
from time import gmtime, strftime
from tkinter import messagebox
import os

path = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(level=logging.INFO,filename="AppLog.log",
                    filemode='a+',)  # Set the logging level to INFO, and write to file

logger = logging.getLogger("Neko")

config = {}

try:
    with open("config.ini") as conf:
        for i in conf.read().splitlines():
            key = i.split("=")[0]
            value = eval(i.split("=")[1])
            config[key] = value
except:
    logger.error(traceback.format_exc())

version = config.get("version",1349139)
fullscreen = config.get("fullscreen",True)
color = config.get("nekocolor","white")
speed = config.get("nekosize",32)/32
actualspeed = config.get("nekospeed",7)
hideicon = config.get("hideicon",True)

def queryMousePosition():
    curx = root.winfo_pointerx() - root.winfo_rootx()
    cury = root.winfo_pointery() - root.winfo_rooty()
    if curx > -1 and cury > -1 and curx < root.winfo_width()+1 \
       and cury < root.winfo_height()+1:
        return (curx, cury)
    else:
        return (root.winfo_width()//2,root.winfo_height()//2)

def convcolor(img, col):
    orig_color = (255, 255, 255, 255)
    try:
        replacement_color = ImageColor.getrgb(col) + (255,)
    except:
        logger.error(traceback.format_exc())
        return img
    data = np.array(img.convert('RGBA'))
    orig_color = np.array(orig_color).reshape(1, 1, -1)
    data[(data == orig_color).all(axis=-1)] = replacement_color
    img2 = Image.fromarray(data, mode='RGBA')
    return img2

def get_mouse_direction(point, mouse_position, threshold):
    x_diff = mouse_position[0] - point[0]
    y_diff = mouse_position[1] - point[1]

    if x_diff > threshold and y_diff > threshold:
        return "SE"
    elif x_diff > threshold and y_diff < -threshold:
        return "NE"
    elif x_diff < -threshold and y_diff > threshold:
        return "SW"
    elif x_diff < -threshold and y_diff < -threshold:
        return "NW"
    elif x_diff > threshold:
        return "E"
    elif x_diff < -threshold:
        return "W"
    elif y_diff > threshold:
        return "S"
    elif y_diff < -threshold:
        return "N"
    else:
        return "still"

def cut(string):
    return string.replace("\\",'/').split("/")[-1]

run = False

root = Tk()
if fullscreen:
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
else:
    sw = 200
    sh = 200

logger.info("Started at "+strftime("%Y-%m-%d %H:%M:%S", gmtime()))

nekox,nekoy = sw//2, sh//2

canvas = Canvas(root,bg="lime", borderwidth=0, highlightthickness=0)

canvas.pack(expand=True,fill=BOTH)

nekosprites = {
    cut(i): ImageTk.PhotoImage(convcolor(Image.open(i), color).resize((config.get("nekosize",32),config.get("nekosize",32)), resample=Image.NEAREST)) for i in glob.glob(path+"/nekoimages/*.png")
}

root.title("Neko")
rgb = ImageColor.getrgb(color)
if rgb[0] < 80 and rgb[1] < 80 and rgb[2] < 80:
    root.title("Neko?")

icon = nekosprites["alert.png"]

root.wm_iconphoto(True, icon)
root.attributes("-topmost", True)
if fullscreen:
    root.attributes('-transparentcolor', 'lime')
    root.attributes("-fullscreen", True)
    if hideicon:
        root.overrideredirect(1)
else:
    canvas.config(bg="lightgrey")
    root.geometry("300x200")
    if config.get('toolwindow', True):
        root.attributes('-toolwindow', True)

me = canvas.create_image(nekox,nekoy,image=nekosprites["still.png"])

frame = 1

canvas.itemconfig(me, image=nekosprites["E2.png"])

mouse = (90,20)
action = get_mouse_direction((nekox,nekoy),mouse,50)
p = tuple(i-c for i,c in zip(mouse,(nekox,nekoy)))
go = tuple(min(x, 20) for x in p)

animspeed = 19 # lower = faster
thr = 22 # Thereshold. Decides on what distance neko should chase mouse

actions = [
    "sleep",
    "downclaw",
    "leftclaw",
    "upclaw",
    "rightclaw",
    "scratch",
    "yawn"
]

def limit(val,lim):
    if val > 10:
        return min(val,lim)
    elif val < 10:
        return -min(-val,lim)
    else:
        return 0

def updanim():
    global frame, action,run
    frame += 1
    if frame > 2:
        frame = 1
        if action.lower() == "yawn":
            action = "still"
            logger.info("Yawned")
        rand = random.random()
        if action.lower() == "still" and rand < 0.2:
            action = random.choice(actions)
            logger.info("Started random action: "+action)
        if action.lower() in ("scratch","sleep","downclaw",
                              "upclaw","leftclaw",
                              "rightclaw") and random.random() < 0.1:
            logger.info("Stopped current action: "+action)
            action = "still"
    # Show alert action, then after some time, chase the mouse
    if get_mouse_direction((nekox, nekoy), mouse, thr) != "still":
        if not run:
            action = "alert"
            logger.info("Going to chase the cursor!")
            canvas.itemconfig(me, image=nekosprites[f"{action}.png"])
            root.update()
            root.after(250)
    if get_mouse_direction((nekox, nekoy), mouse, thr) == "still":
        if run:
            action = "still"
        run = False
    if action.lower() == "alert" or run:
        action = get_mouse_direction((nekox, nekoy), mouse, thr)
        run = True

    if action.lower() not in ("still", "alert"):
        canvas.itemconfig(me, image=nekosprites[f"{action}{int(frame)}.png"])
        if action.lower() == "sleep":
            root.after(300)
        if action.lower() == "yawn":
            root.after(400)
        
    else:
        canvas.itemconfig(me, image=nekosprites[f"{action}.png"])

    root.after(animspeed * 10, updanim)


def update():
    global nekox,nekoy,p,go,mouse
    p = tuple(i-c for i,c in zip(mouse,(nekox,nekoy)))
    go = tuple(limit(x, actualspeed*speed) for x in p)
    if get_mouse_direction((nekox, nekoy), mouse, thr) != "still":
        nekox,nekoy = tuple(i+c for i,c in zip(go,(nekox,nekoy)))
        canvas.move(me, *go)
    mouse = queryMousePosition()
    if mouse == (0,0):
        quitneko()
    root.after(60,update)

def quitneko():
    root.destroy()
    logger.info("Quited.")
    root.quit()
    raise SystemExit()

updanim()
update()

root.mainloop()
