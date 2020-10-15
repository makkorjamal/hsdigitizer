import tkinter as tk
import os
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
        filemenu.add_command(label="Set Parameters", command=lambda: Parameters(parent))
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

class Parameters(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self)
        self.wm_title("Parameters")
        self.spPath = tk.StringVar()
        self.spPath.set('Spectra path not yet set')
        self.lblColor = tk.StringVar()
        self.createWidgets()


    def createWidgets(self):
        self.paramFrame = tk.LabelFrame(self, padx = 5, pady = 5, text = 'Set parameters')

        self.pathFrame = tk.Frame(self.paramFrame, padx = 5, pady = 5)
        self.pathFrame.grid(row = 0, column = 0)
        self.pathLabel = tk.Label(self.paramFrame, padx = 5, pady = 5, bg = 'red',  textvariable = self.spPath)

            
        self.spPathBtn = tk.Button(self.paramFrame, text="Set", highlightbackground="#56B426", command=self.ask_directory)
        self.pathLabel.grid(row = 0, column = 0)
        self.spPathBtn.grid(row = 0, column = 1)

        self.sfitParamFrame = tk.Frame(self.paramFrame, padx = 5, pady = 5)
        self.sfitParamFrame.grid(row = 1, column = 0)
        self.szaLbl = tk.Label(self.sfitParamFrame, text = 'SZA')
        self.szaEntry = tk.Entry(self.sfitParamFrame)
        self.szaLbl.grid(row = 0, column = 0)
        self.szaEntry.grid(row = 0, column = 1)

        self.apoLbl = tk.Label(self.sfitParamFrame, text = 'APO')
        self.apoEntry = tk.Entry(self.sfitParamFrame)
        self.apoLbl.grid(row = 0, column = 2)
        self.apoEntry.grid(row = 0, column = 3)

        self.resLbl = tk.Label(self.sfitParamFrame, text = 'RES')
        self.resEntry = tk.Entry(self.sfitParamFrame)
        self.resLbl.grid(row = 1, column = 0)
        self.resEntry.grid(row = 1, column = 1)

        self.snLbl = tk.Label(self.sfitParamFrame, text = 'S/N')
        self.snEntry = tk.Entry(self.sfitParamFrame)
        self.snLbl.grid(row = 1, column = 2)
        self.snEntry.grid(row = 1, column = 3)

        self.RearthLbl = tk.Label(self.sfitParamFrame, text = 'Rearth')
        self.RearthEntry = tk.Entry(self.sfitParamFrame)
        self.RearthLbl.grid(row = 2, column = 0)
        self.RearthEntry.grid(row = 2, column = 1)

        self.latlonLbl = tk.Label(self.sfitParamFrame, text = 'Lat/Lon')
        self.latlonEntry = tk.Entry(self.sfitParamFrame)
        self.latlonLbl.grid(row = 2, column = 2)
        self.latlonEntry.grid(row = 2, column = 3)

        self.datetimeFrame = tk.Frame(self.paramFrame, padx = 5, pady = 5)
        self.datetimeFrame.grid(row= 2, column = 0)
        self.dtLbl = tk.Label(self.datetimeFrame, text = 'Date/time')
        self.dtEntry = tk.Entry(self.datetimeFrame)
        self.dtLbl.grid(row = 0, column =0)
        self.dtEntry.grid(row = 0, column = 1)

        self.parambtnFrame = tk.Frame(self.paramFrame, padx = 5, pady = 5)
        self.parambtnFrame.grid(row = 3, column = 0)
        self.cancelBtn = tk.Button(self.parambtnFrame, text = 'Cancel', command = self.destroy)
        self.saveBtn = tk.Button(self.parambtnFrame, text = 'Save', command = self.destroy)
        self.cancelBtn.grid(row = 0, column = 0)
        self.saveBtn.grid(row = 0, column = 1)
        self.paramFrame.pack() 

    def ask_directory(self):
        dir_param = {}
        dir_param['initialdir'] = os.path.expanduser('~')#os.environ["HOME"]
        dir_param['mustexist'] = False
        dir_param['parent'] = self
        dir_param['title'] = 'Please select directory'
        result = tk.filedialog.askdirectory(**dir_param)
        self.spPath.set(result)
        self.pathLabel.config(bg = 'green')

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
        """
        Add a frame class that inherits from tk.Frame
        Example: DigiApp(tk.Frame)

        """
        
        tab1 = ttk.Frame(self)
        tab2 = ttk.Frame(self)
        digi_app = DigiApp(root)
        cali_app = CaliApp(root)
        # global cali_gthread = cali_app.get_globals()
        self.add(digi_app, text = "Digitization")
        self.add(cali_app , text = "Calibration")

root = Root()
root.mainloop()
