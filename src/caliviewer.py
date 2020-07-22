from matplotlib.lines import Line2D
import threading
from matplotlib.widgets import SpanSelector
import tkinter as tk
import os
from sklearn.linear_model import LinearRegression
import ttk
import config
import matplotlib.gridspec as gridspec
from scipy.signal import find_peaks
from scipy.signal import detrend
from sklearn.linear_model import LinearRegression
from scipy.signal import savgol_filter, general_gaussian
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
        self.cal_wv = []
        self.cal_pix = []

    def create_widgets(self):
        self.plotframe= tk.LabelFrame(self, padx = 3, pady = 15)
        self.plotframe.grid(row = 0, column = 0)
        screen_dpi = 200 
        self.parent.update()
        plot_width = int(0.80*(self.parent.winfo_width()/screen_dpi))
        plot_height =int( 0.9*(self.parent.winfo_height()/screen_dpi))
        self.fig = Figure(figsize=(plot_width, plot_height), dpi=screen_dpi)
        gs = gridspec.GridSpec(nrows=4, ncols=4, figure=self.fig)

        self.ax = self.fig.add_subplot(gs[0:2,:-1], picker=True)
        self.calax = self.fig.add_subplot(gs[1:3, 3:4])
        self.calax.tick_params(labelsize=3)
        self.ax.tick_params(labelsize=8)
        self.mwax = self.fig.add_subplot(gs[2:4,:-1], picker=True)
        # self.fax = self.ax.twinx()
        # self.fax.tick_params(labelsize=8)
        self.mwax.tick_params(labelsize=8)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plotframe)
        self.canvas.get_tk_widget().grid(row = 0, column = 0)
        self.cid = self.canvas.mpl_connect('button_press_event', self.onclick)
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
        self.cbutton = tk.Button(self.commandframe, text = "Calibrate", command = self.calibrate_sp, padx = 10, pady = 4, font = ("Helvetica", 16))
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
        # self.progressbar = ttk.Progressbar(self.commandframe, mode='indeterminate')
        # self.progressbar.grid(column=4, row=0, sticky=tk.W)
        #peak finder frame
        self.peakframe = tk.LabelFrame(self.commandframe, padx=5, pady=5)
        self.peakframe.grid(row=0, column=5)
        self.sbutton = tk.Button(self.peakframe, text = "Smooth", command = self.smooth_sp, padx = 5, pady = 4, font = ("Helvetica", 16))
        self.sbutton.grid(row = 0, column = 0)
        self.peakbutton = tk.Button(self.peakframe, text = "Peaks", command = self.find_peaks, padx = 5, pady = 4, font = ("Helvetica", 16))
        self.peakbutton.grid(row = 1, column = 0)
        #check spectra frame
        self.checkframe = tk.LabelFrame(self.commandframe, padx=5, pady=5)
        self.checkframe.grid(row=0, column=6)
        self.checkvar1 = tk.IntVar()
        self.checkvar1.set(1)
        self.checkvar2 = tk.IntVar()
        self.checkvar2.set(1)
        self.simulated_checkbtn = tk.Checkbutton(self.checkframe, text='Simulated',variable=self.checkvar1, onvalue=1, offvalue=0, command=self.show_selected)
        self.simulated_checkbtn.pack()
        self.meassured_checkbtn = tk.Checkbutton(self.checkframe, text='Measured',variable=self.checkvar2, onvalue=1, offvalue=0, command=self.show_selected) 
        self.meassured_checkbtn.pack()
        self.span_select = SpanSelector(self.mwax, self.on_pltselect, 'horizontal', useblit=True, rectprops=dict(alpha=0.5, facecolor='red'), button = 3)
    def quit(self):
        self.parent.quit()     # stops mainloop
        self.parent.destroy()  # this is necessary on Windows to prevent

    def calibrate_sp(self):
        cl_fname = '{}_{}'.format(self.sp_range[0], self.sp_range[1]) + '_cal_lines.dat'
        cl_path = os.path.join(self.savepath,cl_fname )
        with open(cl_path, 'w') as f:
            for i, j in zip(self.cal_wv, self.cal_pix):
                f.write('%4.4f %4.4f\n'%(i,j))

        Calibrator(self.savepath, self.spectrum, cl_fname)
        self.threadnm = "cali"

    def start_multip_thread(self, threadnm):

        self.threadnm = threadnm
        if threadnm == "cali":
            self.g_thread = threading.Thread(target=self.calibrate_sp)
            self.cbutton['state'] = tk.DISABLED
        self.g_thread.daemon = True
        # self.progressbar.start()
        self.g_thread.start()
        self.parent.after(20, self.check_g_thread)

    def check_g_thread(self):
        if self.g_thread.is_alive():
            self.parent.after(20, self.check_g_thread)
        else:
            # self.progressbar.stop()
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
            self.ax.clear()
            self.canvas.draw()

        if self.threadnm == "digi":
            self.spectralist.delete(0,tk.END)
            for dx in self.data:
                self.spectralist.insert(tk.END, dx.img_name)

    def on_list_select(self,event):

        self.active = self.spectralist.get(tk.ACTIVE)
        if self.data:
            for od in self.data:
                if self.active == od.calsp_name and self.threadnm == "cali":
                    self.sp_selected = od.calsp_name
                    self.sp_range = od.sp_range
                if self.active == od.img_name and self.threadnm == "digi":
                    self.sp_digi = od.sp_name
                    self.sp_range = od.sp_range
            if self.threadnm == "cali":
                self.pbutton['state'] = "normal"
                # self.canvas.draw()
            elif self.threadnm == "digi":
                self.threadnm = "digi"
                # self.populate_list()
                self.ax.clear()
                self.mwax.clear()
                self.calax.clear()
                self.ax1_lines = []
                self.ax2_lines = []
                self.ini_plot()

    def ini_plot(self):
        self.threadnm = "digi"
        self.mwax.clear()
        self.ax.clear()
        try:
            self.ftir_sp = np.recfromtxt('data/simulated.dat', names=['w', 'i'], encoding='utf8')
            self.ftir_wv = self.ftir_sp.w
            self.ftir_in = self.ftir_sp.i
            self.selectedftir_wv = self.ftir_wv[( self.ftir_wv>(self.sp_range[0]-10) ) & ( self.ftir_wv<(self.sp_range[1] -10))]
            self.selectedftir_in = self.ftir_in[( self.ftir_wv <(self.sp_range[1] -10)) & ( self.ftir_wv>(self.sp_range[0]-10))] 

            self.spectrum = np.loadtxt(os.path.join(self.savepath, self.sp_digi), skiprows=0)
            self.xvals = np.arange(len(self.spectrum))
            # self.spectrum = self.spectrum*(-1) + np.max(self.spectrum)
            self.selectedftir_in = self.selectedftir_in*(-1) + np.max(self.selectedftir_in)
            self.ax.plot(self.selectedftir_in, 'r', linewidth = 0.3)
            self.ax.set_ylim(self.mwax.get_ylim()[::-1])
            self.mwaxline, = self.mwax.plot(self.xvals , self.spectrum, linewidth= 0.3)
            self.mwax.set_ylim(self.mwax.get_ylim()[::-1])
            self.canvas.draw_idle()
        except FileNotFoundError:
            print("File Not found")

    def smooth_sp(self):
        window = 5
        poly_order= 2
        self.smoothed_sp = savgol_filter(self.spectrum, 6*window + 1, poly_order, deriv=0)
        self.mwax.clear()
        self.mwax.plot(self.smoothed_sp, linewidth=0.3)
        self.mwax.set_ylim(self.mwax.get_ylim()[::-1])
        self.canvas.draw_idle()

    def find_peaks(self):
        digi_peaks, _ = find_peaks(self.smoothed_sp, prominence=500)
        sim_peaks, _ = find_peaks(self.selectedftir_in, prominence=0.2)
        ldigi_peaks = digi_peaks[ (digi_peaks > np.min(self.ax2_lines)) & (digi_peaks < np.max(self.ax2_lines)) ]
        lsim_peaks = sim_peaks[ (sim_peaks > np.min(self.ax1_lines)) & (sim_peaks < np.max(self.ax1_lines)) ]
        self.mwax.plot(ldigi_peaks, self.smoothed_sp[ldigi_peaks], "xr")
        # self.ax.plot(lsim_peaks, self.selectedftir_in[lsim_peaks], "xb")
        # reg = LinearRegression().fit(ldigi_peaks.reshape(-1,1),lsim_peaks.reshape(-1,1) )
        # predicted_lsim = reg.predict(digi_peaks.reshape(-1,1))
        # predicted_lsim = predicted_lsim.astype(int)
        self.ax.plot(lsim_peaks, self.selectedftir_in[lsim_peaks], "xb")
        # self.mwax.plot(digi_peaks, self.smoothed_sp[digi_peaks], "xr")
        # self.calax.scatter(ldigi_peaks, self.cal_wv, marker= '.')
        self.calax.scatter(ldigi_peaks, lsim_peaks, marker= 'o')
        # self.calax.scatter(digi_peaks, predicted_lsim, marker= '.')
        self.canvas.draw_idle()
        self.cal_pix = ldigi_peaks
        # predicted_lsim = np.array(predicted_lsim.flatten())
        [self.cal_wv.append(self.selectedftir_wv[i]) for i in lsim_peaks]
        self.cal_wv = np.array(self.cal_wv).round(4)
        print(lsim_peaks)
        print(self.cal_wv)

    def read_cal_spec(self, path, name):

        with open(os.path.join(path, name)) as f:
            lines = f.readlines()
        wl_line = np.fromstring(lines[3], dtype = np.float16, sep = '\t')
        wl_line = wl_line.astype(np.float)
        spec = np.array(lines[4:])
        spec = spec.astype(np.float)
        wavelength = np.linspace(wl_line[0], wl_line[1], int(wl_line[3]))
        return spec, wavelength

    def plot_spectra(self):
        if self.threadnm == "digi":
            self.populate_list()
        #get selected spectra and plot
        elif self.threadnm == "cali":
            try:
                self.spec , self.wavelength = self.read_cal_spec(self.savepath, '{}_{}_calibrated.dat'.format(self.sp_range[0],self.sp_range[1]))
                self.ax.clear()

                self.selectedftir_in = self.selectedftir_in*(-1) + np.max(self.selectedftir_in)
                self.ax.plot(self.selectedftir_wv, self.selectedftir_in, 'r', linewidth = 0.3)
                self.axline, = self.ax.plot(self.wavelength, self.spec / np.max(self.spec), linewidth=0.3)
                self.hscaler.configure(from_ = np.min(self.wavelength), to = np.max(self.wavelength), resolution = 0.01)
                # self.hscaler_p.configure(from_ = self.sp_range[0], to = self.sp_range[1], resolution = 0.01)
                self.mean_wv = (np.min(self.wavelength)+np.max(self.wavelength))/2
                self.hscale_var.set(int(self.mean_wv))
                # self.hscale_var_p.set(int(self.mean_wv))
                self.canvas.draw()
            except FileNotFoundError:
                print('File not found')

    def show_selected(self):
        if (self.checkvar1.get()==1) & (self.checkvar2.get()==0):
            # self.faxline.set_visible(True)
            self.axline.set_visible(False)
            self.canvas.draw()

        if (self.checkvar1.get()==0) & (self.checkvar2.get()==1):

            # self.faxline.set_visible(False)
            self.axline.set_visible(True)
            self.canvas.draw()
        if (self.checkvar1.get()==1) & (self.checkvar2.get()==1):

            # self.faxline.set_visible(True)
            self.axline.set_visible(True)
            self.canvas.draw()

        if (self.checkvar1.get()==0) & (self.checkvar2.get()==0):

            # self.faxline.set_visible(False)
            self.axline.set_visible(False)
            self.canvas.draw()

    def onclick(self, event):
        if event.dblclick:
            if event.inaxes==self.ax:
                self.ax1_lines.append(event.xdata)
                self.ax1l = self.ax.vlines(self.ax1_lines, 0,1, linestyles = 'solid', linewidth = 0.5)
                self.canvas.draw_idle()
            elif event.inaxes==self.mwax:
                self.ax2_lines.append(event.xdata)
                self.ax2l = self.mwax.vlines(self.ax2_lines, 0,1,transform = self.mwax.get_xaxis_transform(), linestyles = 'solid', linewidth = 0.5)
                self.canvas.draw_idle()
            else:
                pass

    def scaleSpectra(self, dummy):
        if self.threadnm == "cali":
            hscale_value = self.hscaler.get()
            hscale_value_p = self.hscaler_p.get()
            vscale_value = self.vscaler.get()
            vscale_value_p = self.vscaler_p.get()
            x_vals =  self.wavelength * (hscale_value/self.mean_wv) + hscale_value_p/self.mean_wv 
            # y_vals = self.spectrum * (vscale_value/50) + (vscale_value_p/50)
            self.axline.set_xdata(x_vals)
            # self.axline.set_ydata(y_vals)
            self.canvas.draw_idle()
        else:
            print("First plot spectra to scale")

    def on_pltselect(self, wv_min, wv_max):

        idxmin, idxmax = np.searchsorted(self.x_vals, (wv_min, wv_max))
        idxmax = min(len(self.x_vals) - 1, idxmax)

        self.xvals = self.x_vals[idxmin:idxmax]
        self.spectrum = self.spectrum[idxmin:idxmax]
        self.mwaxline.set_data(self.xvals, self.spectrum)
        self.mwax.set_xlim(self.xvals[0], self.xvals[-1])
        self.mwax.set_ylim(self.spectrum.min(), self.spectrum.max())
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

