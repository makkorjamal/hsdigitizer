import threading
import tkinter as tk
import os
from config import SpectraConfig
from tkinter import ttk
import numpy as np
#from matplotlib.backends.backend_tkagg import (
#    FigureCanvasTkAgg, NavigationToolbar2Tk)

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# Implement the default Matplotlib key bindings.
from matplotlib.figure import Figure
from digitization import Digitizer
from jsonparser import JsonParser
from config import SpectraConfig
import cv2
from tkinter.messagebox import showerror
class DigiApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.create_widgets()
        self.threadnm = ""
        home = os.path.expanduser('~')
        self.data = []
        self.active = ""
        self.out_dir = ''

    
    def create_widgets(self):

        self.tbframe = tk.LabelFrame(self, padx = 0, pady = 0)
        self.tbframe.grid(row=0, column=0)

        self.plotframe= tk.LabelFrame(self, padx = 10, pady = 10)
        self.plotframe.grid(row = 1, column = 0)
        screen_dpi = 350 
        self.parent.update()
        plot_width = int(0.9*(self.parent.winfo_width()/screen_dpi))
        plot_height =int( 0.9*(self.parent.winfo_height()/screen_dpi))
        fig = Figure(figsize=(plot_width, plot_height), dpi=screen_dpi)
        # t = np.arange(0, 3, .01)
        self.ax = fig.add_subplot(111)
        self.ax.set_title("Digitized Spectra")
        self.canvas = FigureCanvasTkAgg(fig, master=self.plotframe)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row = 0, column = 0)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.tbframe)
        self.toolbar.update()
        self.cid = self.canvas.mpl_connect('Pick', lambda event: click_command(event.xdata, event.ydata))
        self.empty_vbl = tk.Label(self.plotframe, text = "", padx = 10)
        self.empty_vbl.grid(row = 0, column = 1)
        self.empty_hbl = tk.Label(self.plotframe, text = "", pady = 10)
        self.empty_hbl.grid(row = 1, column = 0)
        ####
        self.listframe = tk.LabelFrame(self, padx = 20, pady = 16)
        self.listframe.grid(row = 1, column = 1)
        self.spectralist = tk.Listbox(self.listframe, height = plot_height*10, font = ("Helvetica", 12))
        self.spectralist.pack(side="left", fill="x")
        self.scrollbar = tk.Scrollbar(self.listframe, orient="vertical")
        self.scrollbar.config(command=self.spectralist.yview)
        self.scrollbar.pack(side="left", fill="y")
        self.spectralist.bind('<Double-1>', self.on_list_select)

        ####
       #Digitize 


        self.commandframe = tk.LabelFrame(self, padx = 15, pady = 15)
        self.commandframe.grid(row = 2, column = 0)
        self.dbutton_text = tk.StringVar()
        self.dbutton_text.set("Digitize")
        self.dbutton = tk.Button(self.commandframe, textvariable = self.dbutton_text, command =lambda: self.start_multip_thread("digi"), padx = 10, pady = 4, font = ("Helvetica", 16))
        self.dbutton.grid(row = 0, column = 0)

       #Plot 
        self.pbutton = tk.Button(self.commandframe, text = "Plot", command = self.plot_spectra, padx = 10, pady = 4, font = ("Helvetica", 16))
        self.pbutton.grid(row = 0, column = 2)
        self.pbutton['state'] = tk.DISABLED
       #Quit 
        self.qbutton = tk.Button(self.commandframe, text = "Quit", command = self.quit, padx = 5, pady = 4, font = ("Helvetica", 16))
        self.qbutton.grid(row = 0, column = 3)
        #Progress
        self.progressbar = ttk.Progressbar(self.commandframe, mode='indeterminate')
        self.progressbar.grid(column=4, row=0, sticky=tk.W)
    def quit(self):
        self.parent.quit()     # stops mainloop
        self.parent.destroy()  # this is necessary on Windows to prevent

    def digitize_sp(self):
        """
        This function runs the digitazation process in parallel
        Parameters: 
            dpath: path where the images to be digitized are stored
            base_dir: path where the digitzed .bat file is saved
        """

        try:

            self.base_dir = SpectraConfig.read_conf()['spectra.conf']['spectrapath']
            jsparser = JsonParser(self.base_dir,[])
            self.data = jsparser.read_json('spectra_file.json')
            self.out_dir = os.makedirs(os.path.join(self.base_dir,'digitized/'), exist_ok=True)

        except FileNotFoundError:
            self.data = []
            self.base_dir = ""

        self.dpath = SpectraConfig.read_conf()['spectra.conf']['spectrapath']
        Digitizer(self.base_dir, self.out_dir)

    def start_multip_thread(self, threadnm):
        """
        This function starts a thread to run the progress bar and avoid the UI freeze
        """

        self.g_thread = threading.Thread(target=self.digitize_sp)
        if self.data:
            self.messagebox = tk.messagebox.askquestion("Digitize", "Spectra already digitized, digitize again? ", icon = 'warning')

            if self.messagebox == "yes":
                self.threadnm = threadnm
                self.dbutton['state'] = tk.DISABLED
                self.g_thread.daemon = True
                self.progressbar.start()
                self.g_thread.start()
                self.parent.after(20, self.check_g_thread)
            else:
                self.populate_list()
        else:
            self.threadnm = threadnm
            self.dbutton['state'] = tk.DISABLED
            self.g_thread.daemon = True
            self.progressbar.start()
            self.g_thread.start()
            self.parent.after(20, self.check_g_thread)

    def check_g_thread(self):
        """
        This function checks if the thread is still running and stops the progress when the thread is dead
        """
        try:
            if self.g_thread.is_alive():
                self.parent.after(20, self.check_g_thread)
            else:
                self.progressbar.stop()
                self.populate_list()
        except:
            showerror(title='Parameter Error', message='Paramaters needs to be set up\
                      Go to File > Set Parameters')

    def populate_list(self):
        """
        This fucntion populates the list by reading the json file that contains:
            *the name of the image*
            *the path of the digitzed spectrum*
        """

        jsparser = JsonParser(self.base_dir,[])
        try:
            self.data = jsparser.read_json('spectra_file.json')
        except FileNotFoundError:
            self.data = []
        self.threadnm = "digi"
        if self.threadnm == "digi":
            self.spectralist.delete(0,tk.END)
            self.dbutton['state'] = tk.DISABLED
            for dx in self.data:
                self.spectralist.insert(tk.END, dx.img_name)

    def on_list_select(self,event):
        """
        This function takes the event of double click and select the image
        """

        self.active = self.spectralist.get(tk.ACTIVE)
        if self.data:
            for od in self.data:
                if od.img_name == self.active and self.threadnm == "digi":
                    self.sp_selected = od.sp_name
                    self.img_selected = od.img_name
            if self.threadnm == "digi":
                im_path = os.path.join(self.base_dir,self.img_selected)
                org_img = cv2.imread(im_path,cv2.COLOR_BGR2RGB)
                self.RGB_img = cv2.cvtColor(org_img, cv2.COLOR_BGR2RGB)
                #self.ax.clear()
                self.rgbline = self.ax.imshow(self.RGB_img ,interpolation= None , cmap='viridis',aspect='auto')
                self.canvas.draw()
                self.pbutton['state'] = "normal"
                self.RGB_img = cv2.flip(self.RGB_img, 0)
    
    def plot_spectra(self):
        """
        This function plot the selected spectra on top of the coresponding image

        """
        try:
            if self.threadnm == "digi":
                self.spectrum = np.loadtxt(os.path.join(self.base_dir, self.sp_selected))
            x_vals = np.arange(0,len(self.spectrum))
            self.ax.plot(x_vals,self.spectrum, linewidth = 0.3)
            self.rgbline.set_data(self.RGB_img)
            self.ax.invert_yaxis()
            self.canvas.draw_idle()
        except FileNotFoundError:
            print('File not found')


if __name__ == "__main__":
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.resizable(False, False)
    root.title("Spectra Digitizer")
    root.geometry("{}x{}".format(int(width - 0.2*width),int(height - 0.2*height)))
    DigiApp(root).pack()
    root.mainloop()

