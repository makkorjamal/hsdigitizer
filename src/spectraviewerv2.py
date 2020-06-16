import tkinter as tk
from digiviewer import DigiApp
from caliviewer import CaliApp
import ttk
import config

class Root(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.resizable(False, False)
        self.title("Spectra Digitizer")
        self.geometry("{}x{}".format(int(width - 0.2*width),int(height - 0.2*height)))
        #initialize menu
        self.config(menu=MenuBar(self))
        self.appFrame = Application(self)
        self.appFrame.pack(side='top', fill='both', expand='True')
        self.status = StatusBar(self)
        self.status.pack(side='bottom', fill='x')

class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)
        self.parent = parent
        filemenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="File",underline=0, menu=filemenu)
        filemenu.add_command(label="Set Param", command=self.callback)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", underline=1, command=self.quit)

        helpmenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About...", command=self.callback)

    def quit(self):
        self.parent.quit()     # stops mainloop
        self.parent.destroy()  # this is necessary on Windows to prevent

    def callback(self):
        print(  "Spectra Digitizer" )

class StatusBar(ttk.Frame):

    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.label = ttk.Label(self, relief='sunken', anchor='w')
        self.label.pack(fill='x')

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()

class Application(ttk.Notebook):
    def __init__(self, root):
        ttk.Notebook.__init__(self, root)
        
        tab1 = ttk.Frame(self)
        tab2 = ttk.Frame(self)
        digi_app = DigiApp(root)
        cali_app = CaliApp(root)
        # global cali_gthread = cali_app.get_globals()
        self.add(digi_app, text = "Digitization")
        self.add(cali_app , text = "Calibration")

root = Root()
root.mainloop()
