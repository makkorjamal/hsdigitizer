import tkinter as tk
import os
from digiviewer import DigiApp
from caliviewer import CaliApp
from tkinter import ttk
from config import SpectraConfig

class Root(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        #self.resizable(False, False)
        self.title("Spectra Digitizer")
        self.geometry(f"{int(width)}x{int(height)}")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
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
        helpmenu.add_command(label="About...", command=lambda: About(parent))

    def quit(self):
        self.parent.quit()     # stops mainloop
        self.parent.destroy()  # this is necessary on Windows to prevent

    def callback(self):
        print(  "Spectra Digitizer" )

class Parameters(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self)
        self.entries = {}
        self.counter = 1
        self.wm_title("Parameters")
        self.spPath = tk.StringVar()
        self.spPath.set('Spectra path not yet set')
        self.spRes = tk.DoubleVar()
        self.spRes.set(0.25)
        self.spAPO = tk.StringVar()
        self.spAPO.set('TRI')
        self.spSN = tk.DoubleVar()
        self.spSN.set(100)
        self.spLatlon = tk.StringVar()
        self.spLatlon.set('46.5475, 7.9821')
        self.spSZA = tk.DoubleVar()
        self.spREarth = tk.DoubleVar()
        self.spMinWV = tk.DoubleVar() 
        self.spMaxWV = tk.DoubleVar()
        self.spDT = tk.StringVar()
        self.sTime = tk.StringVar()
        self.eTime = tk.StringVar()
        self.spDT.set('01/01/1951')
        self.sTime.set('00:00')
        self.eTime.set('00:00')

        self.createWidgets()

    def add_field_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Enter Label")
        tk.Label(popup, text="Field Label:").pack(pady=10, padx=10)
        label_entry = tk.Entry(popup)
        label_entry.pack(pady=10, padx=10)
        tk.Button(popup, text="OK", command=lambda: self.create_field(label_entry.get(), popup)).pack(pady=10)


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
        self.szaEntry = tk.Entry(self.sfitParamFrame, textvariable = self.spSZA)
        self.szaLbl.grid(row = 0, column = 0)
        self.szaEntry.grid(row = 0, column = 1)

        self.apoLbl = tk.Label(self.sfitParamFrame, text = 'APO')
        self.apoEntry = tk.Entry(self.sfitParamFrame, textvariable = self.spAPO)
        self.apoLbl.grid(row = 0, column = 2)
        self.apoEntry.grid(row = 0, column = 3)

        self.resLbl = tk.Label(self.sfitParamFrame, text = 'RES')
        self.resEntry = tk.Entry(self.sfitParamFrame, textvariable = self.spRes)
        self.resLbl.grid(row = 1, column = 0)
        self.resEntry.grid(row = 1, column = 1)

        self.snLbl = tk.Label(self.sfitParamFrame, text = 'S/N')
        self.snEntry = tk.Entry(self.sfitParamFrame, textvariable = self.spSN)
        self.snLbl.grid(row = 1, column = 2)
        self.snEntry.grid(row = 1, column = 3)

        self.rearthLbl = tk.Label(self.sfitParamFrame, text = 'Rearth')
        self.rearthEntry = tk.Entry(self.sfitParamFrame, textvariable = self.spREarth)
        self.rearthLbl.grid(row = 2, column = 0)
        self.rearthEntry.grid(row = 2, column = 1)

        self.latlonLbl = tk.Label(self.sfitParamFrame, text = 'Lat/Lon')
        self.latlonEntry = tk.Entry(self.sfitParamFrame, textvariable = self.spLatlon)
        self.latlonLbl.grid(row = 2, column = 2)
        self.latlonEntry.grid(row = 2, column = 3)

        self.minWVLbl = tk.Label(self.sfitParamFrame, text = 'minWL')
        self.minWVEntry = tk.Entry(self.sfitParamFrame, textvariable = self.spMinWV)
        self.minWVLbl.grid(row = 3, column = 0)
        self.minWVEntry.grid(row = 3, column = 1)

        self.maxWVLbl = tk.Label(self.sfitParamFrame, text = 'maxWL')
        self.maxWVEntry = tk.Entry(self.sfitParamFrame, textvariable = self.spMaxWV)
        self.maxWVLbl.grid(row = 3, column = 2)
        self.maxWVEntry.grid(row = 3, column = 3)

        self.datetimeFrame = tk.Frame(self.paramFrame, padx = 0, pady = 0)
        self.datetimeFrame.grid(row= 2, column = 0)

        self.dtLbl = tk.Label(self.datetimeFrame, text = 'Date')
        self.dtEntry = tk.Entry(self.datetimeFrame, textvariable = self.spDT)
        self.dtLbl.grid(row = 0, column =0)
        self.dtEntry.grid(row = 0, column = 1)

        self.sTimeLbl = tk.Label(self.datetimeFrame, text = 'Start Time')
        self.stEntry = tk.Entry(self.datetimeFrame, textvariable = self.sTime)
        self.sTimeLbl.grid(row = 1, column =0)
        self.stEntry.grid(row = 1, column = 1)

        self.eTimeLbl = tk.Label(self.datetimeFrame, text = 'End Time')
        self.etEntry = tk.Entry(self.datetimeFrame, textvariable = self.eTime)
        self.eTimeLbl.grid(row = 2, column =0)
        self.etEntry.grid(row = 2, column = 1)

        self.parambtnFrame = tk.Frame(self.paramFrame, padx = 5, pady = 5)
        self.parambtnFrame.grid(row = 3, column = 0)
        self.cancelBtn = tk.Button(self.parambtnFrame, text = 'Cancel', command = self.destroy)
        self.saveBtn = tk.Button(self.parambtnFrame, text = 'Save', command = self.save_params)
        self.cancelBtn.grid(row = 0, column = 3)
        self.saveBtn.grid(row = 0, column = 2)
        self.newField = tk.Button(self.parambtnFrame, text="New Field", command=self.add_field_popup)
        self.newField.grid(row = 0, column = 1)
        #self.newField.pack(pady=20)
        self.paramFrame.pack()
        print(self.entries)

    def create_field(self, field_label, popup):
        popup.destroy()
        input_variable = tk.StringVar()
        label = tk.Label(self.datetimeFrame, text=field_label)
        entry = tk.Entry(self.datetimeFrame, textvariable=input_variable)
        label.grid(row = 2 + self.counter, column = 0)
        entry.grid(row = 2 + self.counter, column = 1)
        self.entries[field_label] = input_variable
        self.counter += 1

    def ask_directory(self):
        dir_param = {}
        dir_param['initialdir'] = os.path.expanduser('.')#os.environ["HOME"]
        print(os. getcwd())
        dir_param['mustexist'] = False
        dir_param['parent'] = self
        dir_param['title'] = 'Please select directory'
        result = tk.filedialog.askdirectory(**dir_param)
        if result == os.getcwd():
            self.spPath.set('.')
        else:
            self.spPath.set(result)
        if os.path.isdir(self.spPath.get()):
            self.pathLabel.config(bg = 'green')
        else:
            self.pathLabel.config(bg = 'red')
            self.spPath.set('Not a valid directory')

    def save_params(self):
        default = {'Resolution':self.spRes.get(), 'Apodization':self.spAPO.get(), 'SignalToNoise':self.spSN.get(), 
                'Latitude/Longitude':self.spLatlon.get()}
        spconfig = {'SpectraPath':self.spPath.get(), 'SolarZenith':self.spSZA.get(), 'REarth':self.spREarth.get(),
                'MinWavelength':self.spMinWV.get(),'MaxWavelength':self.spMaxWV.get(),'Date':self.spDT.get(),
                'StartTime':self.sTime.get(), 'EndTime':self.eTime.get()}
        if self.entries:
            spconfig ={key: value for key, value in self.entries.items()}
        SpectraConfig.fill_config(default, spconfig)
        self.destroy()


class About(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self)

        self.wm_title("About")
        self.createWidgets()

    def createWidgets(self):
        self.aboutFrame = tk.LabelFrame(self, padx = 5, pady = 5, text = 'About us')
        self.aFrame = tk.Frame(self.aboutFrame, padx = 5, pady = 5)
        self.aFrame.grid(row = 0, column = 0)
        self.info = tk.Label(self.aFrame, text = 'This software allows the extraction and calibration\
                              of spectra printed on paper')
        self.aFrame.pack()

class StatusBar(ttk.Frame):

    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.label = ttk.Label(self, relief='sunken', anchor='w', padding=5)
        self.label.pack(fill='x')
        #self.set('Ready...')

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
        status = StatusBar(self)
        status.set('Ready')
        digi_app = DigiApp(root, status)
        cali_app = CaliApp(root)
        # global cali_gthread = cali_app.get_globals()
        self.add(digi_app, text = "Digitization")
        self.add(cali_app , text = "Calibration")

root = Root()
root.mainloop()
