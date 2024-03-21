from tkinter import *
from tkinter import ttk
import os
from tkinter import colorchooser

path = os.path.dirname(os.path.abspath(__file__))

root = Tk()

color4neko = "#FFFFFF"
nekospeed = DoubleVar(value=7)
nekosize = IntVar(value=32)
fullscreen = IntVar(value=1)
toolwindow = IntVar(value=0)
hideicon = IntVar(value=1)

def setcolor():
    global color4neko
    color4neko = colorchooser.askcolor(title ="Choose color")[1]
    style.configure("color.TButton", background=color4neko, foreground=color4neko)

def apply():
    with open("config.ini","w") as f:
        f.write(template.format(fullscreen.get(),toolwindow.get(),color4neko,nekosize.get(),nekospeed.get(),hideicon.get()))
template = '''fullscreen={}
version=0.5
toolwindow={}
nekocolor="{}"
nekosize={}
nekospeed={}
hideicon={}'''

root.title("NekoCFG")

root.geometry("320x200")

root.wm_iconbitmap(path+"/icon.ico")

style = ttk.Style()
style.theme_use('vista')
style.configure("color.TButton", background=color4neko, foreground=color4neko, relief="flat")


notebook = ttk.Notebook(root)

colortab = Frame(notebook, width=400, height=280)
prop = Frame(notebook, width=400, height=280)
other = Frame(notebook, width=400, height=280)

colortab.pack(fill='both', expand=True, anchor="nw")
prop.pack(fill='both', expand=True, anchor="nw")
other.pack(fill='both', expand=True, anchor="nw")

Label(colortab, text="Color of Neko:").grid(column=1,row=1,sticky=W)
ttk.Button(colortab, text="Set", style="color.TButton", command=setcolor).grid(column=2,row=1)

Label(colortab, text="lazy to add more", fg="grey").grid(column=1,row=2)

Label(prop, text="Neko size (px):").grid(column=1,row=1,sticky=W)
spinbox = ttk.Spinbox(prop,from_=2.0,to=10000, textvariable=nekosize)
spinbox.grid(column=2,row=1)
Label(prop, text="Neko speed (px/upd):").grid(column=1,row=2,sticky=W)
spinbox2 = ttk.Spinbox(prop,from_=1.0,to=100, textvariable=nekospeed)
spinbox2.grid(column=2,row=2)

ttk.Checkbutton(other,text="Tool Window", variable=toolwindow).grid(column=1,row=3,sticky=W)
ttk.Checkbutton(other,text="Hide icon when fullscreen", variable=hideicon).grid(column=1,row=2,sticky=W)
ttk.Checkbutton(other,text="Fullscreen", variable=fullscreen).grid(column=1,row=1,sticky=W)



notebook.add(colortab, text='Customization')
notebook.add(prop, text='Neko properties')
notebook.add(other, text='Other')


notebook.pack(fill='both', expand=True)

root.resizable(False,False)


ttk.Button(text="Apply",command=apply).pack(side=RIGHT)

root.mainloop()
