import threading
import tkinter as tk
import os
import ttk
import sp_globals
import numpy as np
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.figure import Figure
from jsonparser import JsonParser
import cv2
from calibration import Calibrator

class CaliApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.create_widgets()
        self.data = []
        self.x_vals = []
        self.threadnm = ""
        self.savepath = 'data/'
        home = os.path.expanduser('~')
        self.active = ""
        self.dpath = '/mnt/740617C970FA5889/scroll1_21_aout'
        # self.dpath = os.path.join(home,'spectra/')
    
    def create_widgets(self):
        self.plotframe= tk.LabelFrame(self, padx = 10, pady = 15)
        self.plotframe.grid(row = 0, column = 0)
        screen_dpi = 200 
        self.parent.update()
        plot_width = int(0.9*(self.parent.winfo_width()/screen_dpi))
        plot_height =int( 0.9*(self.parent.winfo_height()/screen_dpi))
        fig = Figure(figsize=(plot_width, plot_height), dpi=screen_dpi)
        # t = np.arange(0, 3, .01)
        self.ax = fig.add_subplot(111)
        self.ax.set_title("Calibrated Spectra")
        self.canvas = FigureCanvasTkAgg(fig, master=self.plotframe)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row = 0, column = 0)
        ####
        self.listframe = tk.LabelFrame(self, padx = 20, pady =16)
        self.listframe.grid(row = 0, column = 1)
        self.spectralist = tk.Listbox(self.listframe, height = plot_height*10, font = ("Helvetica", 12))
        self.spectralist.pack(side="left", fill="x")
        self.scrollbar = tk.Scrollbar(self.listframe, orient="vertical")
        self.scrollbar.config(command=self.spectralist.yview)
        self.scrollbar.pack(side="left", fill="y")
        self.spectralist.bind('<Double-1>', self.on_list_select)

        ####
       #Calibrate 


        self.commandframe = tk.LabelFrame(self, padx = 15, pady = 15)
        self.commandframe.grid(row = 1, column = 0)
        self.cbutton = tk.Button(self.commandframe, text = "Calibrate", command = lambda: self.start_multip_thread("cali"), padx = 10, pady = 4, font = ("Helvetica", 16))
        self.cbutton.grid(row = 0, column = 1)

       #Plot 
        self.pbutton = tk.Button(self.commandframe, text = "Plot", command = self.plot_spectra, padx = 10, pady = 4, font = ("Helvetica", 16))
        self.pbutton.grid(row = 0, column = 2)
        self.pbutton['state'] = tk.DISABLED

        self.hscale_var = tk.DoubleVar()
        self.hscale_var.set(50)
        self.hscaler = tk.Scale(self.plotframe, from_=1, to=100, command=self.scaleSpectra, variable=self.hscale_var, orient=tk.HORIZONTAL, length= 300)
        self.hscaler.grid(row = 1, column = 0)

        self.vscale_var = tk.DoubleVar()
        self.vscale_var.set(50)
        self.vscaler = tk.Scale(self.plotframe, from_=1, to=100, command=self.scaleSpectra, variable=self.vscale_var, orient=tk.VERTICAL, length= 300)
        self.vscaler.grid(row = 0, column = 1)
       #Quit 
        self.qbutton = tk.Button(self.commandframe, text = "Quit", command = self.quit, padx = 5, pady = 4, font = ("Helvetica", 16))
        self.qbutton.grid(row = 0, column = 3)
        #Progress
        self.progressbar = ttk.Progressbar(self.commandframe, mode='indeterminate')
        self.progressbar.grid(column=4, row=0, sticky=tk.W)
    def quit(self):
        self.parent.quit()     # stops mainloop
        self.parent.destroy()  # this is necessary on Windows to prevent

    def calibrate_sp(self):

        Calibrator(self.savepath, self.savepath)

    def start_multip_thread(self, threadnm):

        self.threadnm = threadnm
        if threadnm == "cali":
            self.g_thread = threading.Thread(target=self.calibrate_sp)
            sp_globals.cal_gthread = self.g_thread
            self.cbutton['state'] = tk.DISABLED
        self.g_thread.daemon = True
        self.progressbar.start()
        self.g_thread.start()
        self.parent.after(20, self.check_g_thread)

    def check_g_thread(self):
        if self.g_thread.is_alive():
            self.parent.after(20, self.check_g_thread)
        else:
            self.progressbar.stop()
            self.populate_list(self.dpath)

    def populate_list(self,dpath):

        if self.threadnm == "cali":
            self.spectralist.delete(0,tk.END)
            self.cbutton['state'] = tk.DISABLED
            jsparser = JsonParser(self.savepath,[])
            self.data = jsparser.read_json('spectra_file.json')
            for dx in self.data:
                self.spectralist.insert(tk.END, dx.calsp_name)
                print(dx.calsp_name)
            self.ax.clear()
            self.canvas.draw()
    def on_list_select(self,event):

        self.active = self.spectralist.get(tk.ACTIVE)
        if self.data:
            for od in self.data:
                if self.active == od.calsp_name and self.threadnm == "cali":
                    self.sp_selected = od.calsp_name
            if self.threadnm == "cali":
                self.pbutton['state'] = "normal"
                # self.canvas.draw()

    def plot_spectra(self):
        #get selected spectra and plot
        try:
            if self.threadnm == "cali":
                self.spectrum = np.loadtxt(os.path.join(self.savepath, self.sp_selected), skiprows=4)
                self.ax.clear()
            self.x_vals = np.arange(0,len(self.spectrum))
            self.line, = self.ax.plot(self.x_vals,self.spectrum, linewidth = 0.3)
            self.canvas.draw()
        except FileNotFoundError:
            print('File not found')

    def scaleSpectra(self, dummy):
        if self.threadnm == "cali":
            hscale_value = self.hscaler.get()
            vscale_value = self.vscaler.get()
            x_vals =  self.x_vals * (hscale_value/50)
            y_vals = self.spectrum * (vscale_value/50)
            # self.ax.plot(self.x_vals,self.spectrum, linewidth = 0.3)
            self.line.set_xdata(x_vals)
            self.line.set_ydata(y_vals)
            self.canvas.draw_idle()
        else:
            print("First plot spectra to scale")
            print(self.hscaler.get())


if __name__ == "__main__":
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.resizable(False, False)
    root.title("Spectra Digitizer")
    root.geometry("{}x{}".format(int(width - 0.2*width),int(height - 0.2*height)))
    CaliApp(root).pack()
    root.mainloop()

