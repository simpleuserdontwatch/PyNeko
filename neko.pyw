from tkinter import *
from PIL import Image, ImageTk
import glob
import logging
import random
from time import gmtime, strftime
reqs = True
try:
    import requests
except:
    reqs = False
from tkinter import messagebox

config = {}

with open("config.ini") as conf:
    for i in conf.read().splitlines():
        key = i.split("=")[0]
        value = eval(i.split("=")[1])
        config[key] = value
        
version = config["version"]
fullscreen = config["fullscreen"]

def queryMousePosition():
    x = root.winfo_pointerx() - root.winfo_rootx()
    y = root.winfo_pointery() - root.winfo_rooty()
    if x > -1 and y > -1 and x < root.winfo_width()+1 and y < root.winfo_height()+1:
        return (x, y)
    else:
        return (root.winfo_width()//2,root.winfo_height()//2)
        

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
if fullscreen:
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
else:
    sw = 200
    sh = 200

logging.basicConfig(level=logging.INFO,filename="AppLog.log",
                    filemode='w',)  # Set the logging level to INFO, and write to file

frame = 1

logger = logging.getLogger("Neko")
logger.info("Started at "+strftime("%Y-%m-%d %H:%M:%S", gmtime()))

nekox,nekoy = sw//2, sh//2

canvas = Canvas(root,bg="lime", borderwidth=0, highlightthickness=0)

canvas.pack(expand=True,fill=BOTH)

nekosprites = {
    cut(i): ImageTk.PhotoImage(Image.open(i)) for i in glob.glob("nekoimages/*.png")
}

icon = nekosprites["still.png"]


root.title("Neko")
root.wm_iconphoto(True, icon)
root.attributes("-topmost", True)
if fullscreen:
    root.attributes('-transparentcolor', 'lime')
    root.attributes("-fullscreen", True)
else:
    canvas.config(bg="lightgrey")
    root.geometry("300x200")

me = canvas.create_image(nekox,nekoy,image=nekosprites["still.png"])

canvas.itemconfig(me, image=nekosprites["E2.png"])

mouse = (90,20)
action = get_mouse_direction((nekox,nekoy),mouse,50)
p = tuple(i-c for i,c in zip(mouse,(nekox,nekoy)))
go = tuple(min(x, 20) for x in p)

animspeed = 20 # lower = faster
thr = 17 # Thereshold. Decides on what distance neko should chase mouse

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
        if action.lower() == "still" and rand < 0.3:  # Doesnt even do anything? Stays always false??
            action = random.choice(actions)
            logger.info("Started random action: "+action)
        if action.lower() in ("scratch","sleep","downclaw","upclaw","leftclaw","rightclaw") and random.random() < 0.1:
            logger.info("Stopped current action: "+action)
            action = "still"
    # Show alert action, then after some time, chase the mouse
    if get_mouse_direction((nekox, nekoy), mouse, thr) != "still":
        if not run:
            action = "alert"
            logger.info("Going to chase the cursor!")
            canvas.itemconfig(me, image=nekosprites[f"{action}.png"])
            root.update()
            root.after(300)
    if get_mouse_direction((nekox, nekoy), mouse, thr) == "still":
        if run:
            action = "still"
        run = False
    if action.lower() == "alert" or run:
        action = get_mouse_direction((nekox, nekoy), mouse, thr)
        run = True

    if action.lower() not in ("still", "alert"):
        canvas.itemconfig(me, image=nekosprites[f"{action}{int(frame)}.png"])
        if action.lower() in ("yawn", "sleep"):
            root.after(200)
    else:
        canvas.itemconfig(me, image=nekosprites[f"{action}.png"])
    
    root.after(animspeed * 10, updanim)


def update():
    global nekox,nekoy,p,go,mouse
    p = tuple(i-c for i,c in zip(mouse,(nekox,nekoy)))
    go = tuple(limit(x, 10) for x in p)
    if get_mouse_direction((nekox, nekoy), mouse, thr) != "still":
        nekox,nekoy = tuple(i+c for i,c in zip(go,(nekox,nekoy)))
        canvas.move(me, *go)
    mouse = queryMousePosition()
    root.after(100,update)

def home():
    global mouse
    mouse = (-100,-100)
    root.after(10,home)

def sleep():
    global action
    if action == "still":
        action = "sleep"
    root.after(animspeed * 9, sleep)

def quitneko():
    root.destroy()
    logger.info("Quited.")

def checkupd():
    r = requests.get("https://raw.githubusercontent.com/simpleuserdontwatch/PyNeko/main/neko.pyw")
    ver = requests.get("https://raw.githubusercontent.com/simpleuserdontwatch/PyNeko/main/version.txt")
    if float(ver.text.split('\n')[0]) > version:
        messagebox.showinfo(title="Neko",message="Yay! An new update is available!")
        if messagebox.askquestion("Neko",message="Do you want to download it into other file?") == "yes":
            with open("update.pyw","a+") as f:
                f.write(r.text)
    else:
        messagebox.showinfo(title="Neko",message="No updates.")
def checkupdstart():
    r = requests.get("https://raw.githubusercontent.com/simpleuserdontwatch/PyNeko/main/neko.pyw")
    ver = requests.get("https://raw.githubusercontent.com/simpleuserdontwatch/PyNeko/main/version.txt")
    if float(ver.text.split('\n')[0]) > version:
        messagebox.showinfo(title="Neko",message="Yay! An new update is available!")
        if messagebox.askquestion("Neko",message="Do you wish to download it into other file?") == "yes":
            with open("update.pyw","a+") as f:
                f.write(r.text)

if reqs:  
    checkupdstart()

neko_menu = Menu(tearoff=0)
if reqs:
    neko_menu.add_command(label="Check for update",command=checkupd)
neko_menu.add_command(label="Send him to his house",command=home)
neko_menu.add_command(label="Sleep",command=sleep)
neko_menu.add_command(label="Quit",command=quitneko)


def showMenu(e):
    neko_menu.post(e.x_root, e.y_root)

canvas.tag_bind(me, '<Button-1>', showMenu)

updanim()
update()

root.mainloop()
