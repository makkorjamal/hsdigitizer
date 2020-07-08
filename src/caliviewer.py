from matplotlib.lines import Line2D
import threading
from matplotlib.widgets import SpanSelector
import tkinter as tk
import os
import ttk
import config
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
        self.dpath = ''
        self.threadnm = "digi"
        self.ax1_lines = []
        self.ax2_lines = []

    def create_widgets(self):
        self.plotframe= tk.LabelFrame(self, padx = 3, pady = 15)
        self.plotframe.grid(row = 0, column = 0)
        screen_dpi = 200 
        self.parent.update()
        plot_width = int(0.80*(self.parent.winfo_width()/screen_dpi))
        plot_height =int( 0.9*(self.parent.winfo_height()/screen_dpi))
        self.fig = Figure(figsize=(plot_width, plot_height), dpi=screen_dpi)
        # t = np.arange(0, 3, .01)
        self.ax = self.fig.add_subplot(211, picker=True)
        self.ax.tick_params(labelsize=8)
        self.mwax = self.fig.add_subplot(212, picker=True)
        self.fax = self.ax.twinx()
        self.fax.tick_params(labelsize=8)
        self.mwax.tick_params(labelsize=8)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plotframe)
        self.canvas.get_tk_widget().grid(row = 0, column = 0)
        self.cid = self.canvas.mpl_connect('Pick', lambda event: click_command(event.xdata, event.ydata))
        ####
        self.listframe = tk.LabelFrame(self, padx = 20, pady =16)
        self.listframe.grid(row = 0, column = 1)
        self.spectralist = tk.Listbox(self.listframe, height = plot_height*10, font = ("Helvetica", 12))
        self.spectralist.pack(side="left", fill="x")
        self.scrollbar = tk.Scrollbar(self.listframe, orient="vertical")
        self.scrollbar.config(command=self.spectralist.yview)
        self.scrollbar.pack(side="left", fill="y")
        # self.populate_list()
        self.spectralist.bind('<Double-1>',  self.on_list_select)

        ####
       #Calibrate 


        self.commandframe = tk.LabelFrame(self, padx = 15, pady = 15)
        self.commandframe.grid(row = 1, column = 0)
        self.cbutton = tk.Button(self.commandframe, text = "Calibrate", command = lambda: self.start_multip_thread("cali"), padx = 10, pady = 4, font = ("Helvetica", 16))
        self.cbutton.grid(row = 0, column = 1)

       #Plot 
        self.pbutton = tk.Button(self.commandframe, text = "Plot", command = lambda: self.plot_spectra(), padx = 10, pady = 4, font = ("Helvetica", 16))
        self.pbutton.grid(row = 0, column = 2)
        # self.pbutton['state'] = tk.DISABLED

        self.hscale_var = tk.DoubleVar()
        self.hscale_var.set(50)
        self.hscaler = tk.Scale(self.plotframe, from_=1, to=100, command=self.scaleSpectra, variable=self.hscale_var, orient=tk.HORIZONTAL, length= 300)
        self.hscaler.grid(row = 1, column = 0)

        self.hscale_var_p = tk.DoubleVar()
        self.hscale_var_p.set(50)
        self.hscaler_p = tk.Scale(self.plotframe, from_=1, to=100, command=self.scaleSpectra, variable=self.hscale_var_p, orient=tk.HORIZONTAL, length= 300)
        self.hscaler_p.grid(row = 2, column = 0)

        self.vscale_var = tk.DoubleVar()
        self.vscale_var.set(50)
        self.vscaler = tk.Scale(self.plotframe, from_=1, to=100, command=self.scaleSpectra, variable=self.vscale_var, orient=tk.VERTICAL, length= 300, resolution = 0.1)
        self.vscaler.grid(row = 0, column = 1)

        self.vscale_var_p = tk.DoubleVar()
        self.vscale_var_p.set(0)
        self.vscaler_p = tk.Scale(self.plotframe, from_=50, to=-50, command=self.scaleSpectra, variable=self.vscale_var_p, orient=tk.VERTICAL, length= 300, resolution = 0.1)
        self.vscaler_p.grid(row = 0, column = 2)
       #Quit 
        self.qbutton = tk.Button(self.commandframe, text = "Quit", command = self.quit, padx = 5, pady = 4, font = ("Helvetica", 16))
        self.qbutton.grid(row = 0, column = 3)
        #Progress
        self.progressbar = ttk.Progressbar(self.commandframe, mode='indeterminate')
        self.progressbar.grid(column=4, row=0, sticky=tk.W)
        self.checkframe = tk.LabelFrame(self.commandframe, padx=5, pady=5)
        self.checkframe.grid(row=0, column=5)
        self.checkvar1 = tk.IntVar()
        self.checkvar1.set(1)
        self.checkvar2 = tk.IntVar()
        self.checkvar2.set(1)
        self.simulated_checkbtn = tk.Checkbutton(self.checkframe, text='Simulated',variable=self.checkvar1, onvalue=1, offvalue=0, command=self.show_selected)
        self.simulated_checkbtn.pack()
        self.meassured_checkbtn = tk.Checkbutton(self.checkframe, text='Measured',variable=self.checkvar2, onvalue=1, offvalue=0, command=self.show_selected) 
        self.meassured_checkbtn.pack()
    def quit(self):
        self.parent.quit()     # stops mainloop
        self.parent.destroy()  # this is necessary on Windows to prevent

    def calibrate_sp(self):

        Calibrator(self.savepath, self.savepath)

    def start_multip_thread(self, threadnm):

        self.threadnm = threadnm
        if threadnm == "cali":
            self.g_thread = threading.Thread(target=self.calibrate_sp)
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
            self.populate_list()

    def populate_list(self):

        jsparser = JsonParser(self.savepath,[])
        try:
            self.data = jsparser.read_json('spectra_file.json')
        except FileNotFoundError:
            self.data = []
        if self.threadnm == "cali":
            self.spectralist.delete(0,tk.END)
            self.cbutton['state'] = tk.DISABLED
            for dx in self.data:
                self.spectralist.insert(tk.END, dx.calsp_name)
                print(dx.calsp_name)
            self.ax.clear()
            self.canvas.draw()

        if self.threadnm == "digi":
            self.spectralist.delete(0,tk.END)
            for dx in self.data:
                self.spectralist.insert(tk.END, dx.img_name)
                # print(dx.sp_name)

    def on_list_select(self,event):

        self.active = self.spectralist.get(tk.ACTIVE)
        print(self.active)
        if self.data:
            for od in self.data:
                if self.active == od.calsp_name and self.threadnm == "cali":
                    self.sp_selected = od.calsp_name
                    self.sp_range = od.sp_range
                if self.active == od.img_name and self.threadnm == "digi":
                    self.sp_digi = od.sp_name
                    self.sp_range = od.sp_range
                    print(self.sp_digi)
            if self.threadnm == "cali":
                self.pbutton['state'] = "normal"
                # self.canvas.draw()
                self.hscaler.configure(from_ = self.sp_range[0], to = self.sp_range[1], resolution = 0.01)
                self.hscaler_p.configure(from_ = self.sp_range[0], to = self.sp_range[1], resolution = 0.01)
                self.mean_wv = (self.sp_range[0]+self.sp_range[1])/2
                self.hscale_var.set(int(self.mean_wv))
                self.hscale_var_p.set(int(self.mean_wv))
            elif self.threadnm == "digi":
                self.threadnm = "digi"
                # self.populate_list()
                self.ini_plot()

    def ini_plot(self):
        self.threadnm = "digi"
        self.mwax.clear()
        try:
            self.ftir_sp = np.recfromtxt('data/simulated.dat', names=['w', 'i'], encoding='utf8')
            self.ftir_wv = self.ftir_sp.w
            self.ftir_in = self.ftir_sp.i

            self.spectrum = np.loadtxt(os.path.join(self.savepath, self.sp_digi), skiprows=0)
            self.ax.plot(self.ftir_wv[( self.ftir_wv>self.sp_range[0] ) & ( self.ftir_wv<self.sp_range[1])], (self.ftir_in[( self.ftir_wv <self.sp_range[1]) & ( self.ftir_wv>self.sp_range[0] )]), 'r', linewidth = 0.3, picker=True)
            self.mwax.plot( self.spectrum, linewidth= 0.3, picker=True)
            self.mwax.set_ylim(self.mwax.get_ylim()[::-1])
            self.canvas.draw_idle()
        except FileNotFoundError:
            print("File Not found")
            


    def plot_spectra(self):
        if self.threadnm == "digi":
            self.populate_list()
        #get selected spectra and plot
        elif self.threadnm == "cali":
            try:

                self.ftir_sp = np.recfromtxt('data/simulated.dat', names=['w', 'i'], encoding='utf8')
                self.ftir_wv = self.ftir_sp.w
                self.ftir_in = self.ftir_sp.i
                self.spectrum = np.loadtxt(os.path.join(self.savepath, self.sp_selected), skiprows=4)
                self.ax.clear()
                self.fax.clear()
                self.mwax.clear()
                self.x_vals = np.linspace(self.sp_range[0],self.sp_range[1],len(self.spectrum))
                self.axline, = self.ax.plot(self.x_vals,self.spectrum, picker=5, linewidth = 0.3)
                self.ax.set_ylabel('I', picker=True, bbox=dict(facecolor='red'))
                self.mwaxline, = self.mwax.plot(self.x_vals,self.spectrum, linewidth = 0.3)
                self.faxline, =self.fax.plot(self.ftir_wv[( self.ftir_wv>self.sp_range[0] ) & ( self.ftir_wv<self.sp_range[1])], (self.ftir_in[( self.ftir_wv <self.sp_range[1]) & ( self.ftir_wv>self.sp_range[0] )]), 'r', linewidth = 0.3)
                self.fax.legend([ 'Simulated' ], loc = 'upper right', fontsize='xx-small')
                self.ax.set_zorder(self.fax.get_zorder()+1)
                self.ax.patch.set_visible(False)
                self.span_select = SpanSelector(self.ax, self.on_pltselect, 'horizontal', useblit=True, rectprops=dict(alpha=0.5, facecolor='red'))
                self.ax.legend([ 'Measured' ], loc = 'lower right', fontsize='xx-small')
                self.canvas.draw()
            except FileNotFoundError:
                print('File not found')
    def show_selected(self):
        if (self.checkvar1.get()==1) & (self.checkvar2.get()==0):
            self.faxline.set_visible(True)
            self.axline.set_visible(False)
            self.canvas.draw()

        if (self.checkvar1.get()==0) & (self.checkvar2.get()==1):

            self.faxline.set_visible(False)
            self.axline.set_visible(True)
            self.canvas.draw()
        if (self.checkvar1.get()==1) & (self.checkvar2.get()==1):

            self.faxline.set_visible(True)
            self.axline.set_visible(True)
            self.canvas.draw()

        if (self.checkvar1.get()==0) & (self.checkvar2.get()==0):

            self.faxline.set_visible(False)
            self.axline.set_visible(False)
            self.canvas.draw()

    def plotlines(self):
        self.ax1l = self.ax.vlines(self.ax1_lines, 0,1)
        self.ax2l = self.mwax.vlines(self.ax2_lines, 0,1)
        self.canvas.draw_idle()

    def on_pick(self,event):
        print('you picked:',event.artist)

    def onclick(self, event):
        if event.dblclick:
            if event.inaxes==self.ax:
                self.ax1_lines.append(event.xdata)
            elif event.inaxes==self.mwax:
                self.ax2_lines.append(event.xdata)
            else:
                pass
            print(self.ax1_lines, self.ax2_lines)
            self.plotlines()
    def onpick_ax(self, event):
        if isinstance(event.artist, Line2D):
            thisline = event.artist
            xdata = thisline.get_xdata()
            ydata = thisline.get_ydata()
            ind = event.ind
            print ( 'X='+str(np.take(xdata, ind)[0]) ) # Print X point
            print ( 'Y='+str(np.take(ydata, ind)[0]) ) # Print Y point

    def scaleSpectra(self, dummy):
        if self.threadnm == "cali":
            hscale_value = self.hscaler.get()
            hscale_value_p = self.hscaler_p.get()
            vscale_value = self.vscaler.get()
            vscale_value_p = self.vscaler_p.get()
            x_vals =  self.x_vals * (hscale_value/self.mean_wv) + hscale_value_p/self.mean_wv 
            y_vals = self.spectrum * (vscale_value/50) + (vscale_value_p/50)
            self.axline.set_xdata(x_vals)
            self.axline.set_ydata(y_vals)
            self.canvas.draw_idle()
        else:
            print("First plot spectra to scale")
            print(self.hscaler.get())

    def on_pltselect(self, wv_min, wv_max):

        idxmin, idxmax = np.searchsorted(self.x_vals, (wv_min, wv_max))
        idxmax = min(len(self.x_vals) - 1, idxmax)

        mw_wv = self.x_vals[idxmin:idxmax]
        mw_spec = self.spectrum[idxmin:idxmax]
        self.mwaxline.set_data(mw_wv, mw_spec)
        self.mwax.set_xlim(mw_wv[0], mw_wv[-1])
        self.mwax.set_ylim(mw_spec.min(), mw_spec.max())
        self.canvas.draw_idle()

        # save
        np.savetxt("microwindows/MicroWindow_{:.2f}_{:.2f}.dat".format(min(mw_wv),max(mw_wv)), np.c_[mw_wv, mw_spec], fmt='%1.2f %1.2f')
    
if __name__ == "__main__":
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.resizable(False, False)
    root.title("Spectra Digitizer")
    root.geometry("{}x{}".format(int(width - 0.2*width),int(height - 0.2*height)))
    CaliApp(root).pack()
    root.mainloop()

