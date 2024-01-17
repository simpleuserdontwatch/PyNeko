from ctypes import windll, Structure, c_long, byref, CDLL
from tkinter import *
from PIL import Image, ImageTk
import glob
import os
import logging
import random

if os.name != "nt": # gotta support linux bros :thumbs-up:
    Xlib = CDLL("libX11.so.6")

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]


def queryMousePosition():
    if os.name == "nt": # Windows
        pt = POINT()
        windll.user32.GetCursorPos(byref(pt))
        return (pt.x, pt.y)
    else: # LinLinux
        display = Xlib.XOpenDisplay(None)
        if display == 0: sys.exit(2)
        w = Xlib.XRootWindow(display, c_int(0))
        (root_id, child_id) = (c_uint32(), c_uint32())
        (root_x, root_y, win_x, win_y) = (c_int(), c_int(), c_int(), c_int())
        mask = c_uint()
        ret = Xlib.XQueryPointer(display, c_uint32(w), byref(root_id), byref(child_id),
                                 byref(root_x), byref(root_y),
                                 byref(win_x), byref(win_y), byref(mask))
        if ret == 0: sys.exit(1)
        return (root_x, root_y)
        

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
    return string.replace('nekoimages/','').replace('nekoimages\\','')

run = False

root = Tk()
sw = root.winfo_screenwidth()
sh = root.winfo_screenheight()

logging.basicConfig(level=logging.INFO)  # Set the logging level to INFO

frame = 1

logger = logging.getLogger("Neko")
logger.info("Hi! I'm neko!")
logger.info("You probably just grabbed the source code.")
logger.info("But it's okay!")
logger.info("Remember, please. Don't steal my program, referring to it as yours!")

nekox,nekoy = sw//2, sh//2

canvas = Canvas(root,bg="lime", borderwidth=0, highlightthickness=0)

canvas.pack(expand=True,fill=BOTH)

nekosprites = {
    cut(i): ImageTk.PhotoImage(Image.open(i)) for i in glob.glob("nekoimages/*.png")
}

icon = nekosprites["still.png"]


root.title("Windows Neko")
root.wm_iconphoto(True, icon)
root.attributes("-topmost", True)
root.attributes('-transparentcolor', 'lime')
root.attributes("-fullscreen", True)

me = canvas.create_image(nekox,nekoy,image=nekosprites["still.png"])

canvas.itemconfig(me, image=nekosprites["E2.png"])

mouse = (90,20)
action = get_mouse_direction((nekox,nekoy),mouse,50)
p = tuple(i-c for i,c in zip(mouse,(nekox,nekoy)))
go = tuple(min(x, 20) for x in p)

animspeed = 20 # lower = faster

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
        rand = random.random()
        print(rand)
        if action.lower() == "still" and rand < 0.3:  # Doesnt even do anything? Stays always false??
            action = random.choice(actions)
            print(action)
        if action.lower() in ("scratch","sleep","downclaw","upclaw","leftclaw","rightclaw") and random.random() < 0.1:
            action = "still"
    # Show alert action, then after some time, chase the mouse
    if get_mouse_direction((nekox, nekoy), mouse, 20) != "still":
        if not run:
            action = "alert"
            canvas.itemconfig(me, image=nekosprites[f"{action}.png"])
            root.update()
            root.after(400)
    if get_mouse_direction((nekox, nekoy), mouse, 20) == "still":
        if run:
            action = "still"
        run = False
    if action.lower() == "alert" or run:
        action = get_mouse_direction((nekox, nekoy), mouse, 20)
        run = True

    if action.lower() not in ("still", "alert"):
        canvas.itemconfig(me, image=nekosprites[f"{action}{int(frame)}.png"])
    else:
        canvas.itemconfig(me, image=nekosprites[f"{action}.png"])
    
    root.after(animspeed * 10, updanim)


def update():
    global nekox,nekoy,p,go,mouse
    p = tuple(i-c for i,c in zip(mouse,(nekox,nekoy)))
    go = tuple(limit(x, 10) for x in p)
    nekox,nekoy = tuple(i+c for i,c in zip(go,(nekox,nekoy)))
    canvas.move(me, *go)
    mouse = queryMousePosition()
    root.after(100,update)

updanim()
update()

root.mainloop()
