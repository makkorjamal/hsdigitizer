import datetime
import threading
import tkinter as tk
import os
from config import SpectraConfig
from pybaselines import Baseline
import matplotlib.gridspec as gridspec
from scipy.signal import find_peaks
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# Implement the default Matplotlib key bindings.
from matplotlib.figure import Figure
from jsonparser import JsonParser
from pysolar.solar import *
from calibration import Calibrator
from tkinter.messagebox import showerror, showinfo


class CaliApp(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.create_widgets()
        self.data = []
        self.pixel_xvals = []
        self.threadnm = ""
        self.savepath = ""
        self.active = ""
        self.threadnm = "digi"
        self.ax1_lines = []
        self.ax2_lines = []
        self.cal_wv = []
        self.cal_pix = []
        self.wave_range = []
        self.peak_is_found = False
        self.spectra = []
        self.wavelength = []

    def create_widgets(self):
        self.top_frame = tk.Frame(self)
        self.tbframe = tk.LabelFrame(self.top_frame, padx = 0, pady = 0)
        self.tbframe.grid(row=0, column=0)

        self.plotframe = tk.LabelFrame(self.top_frame, padx=3, pady=10)
        self.plotframe.grid(row=1, column=0)
        screen_dpi = 350
        self.parent.update()
        plot_width = int(0.9 * (self.parent.winfo_width() / screen_dpi))
        plot_height = int(0.9 * (self.parent.winfo_height() / screen_dpi))
        self.fig = Figure(figsize=(plot_width, plot_height), dpi=screen_dpi)
        gs = gridspec.GridSpec(nrows=4, ncols=5, figure=self.fig)

        self.ax = self.fig.add_subplot(gs[0:2, :4], picker=True)
        self.calax = self.fig.add_subplot(gs[1:3, 4:5])
        self.calax.tick_params(labelsize=3, labelrotation = 45)
        self.ax.tick_params(labelsize=5)
        self.mwax = self.fig.add_subplot(gs[2:4, :4], picker=True)
        # self.fax = self.ax.twinx()
        self.ax.tick_params(labelsize=5, axis='x')
        self.ax.xaxis.set_ticks_position('top')
        self.calax.yaxis.set_ticks_position('right')
        self.mwax.tick_params(labelsize=5)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plotframe)
        self.canvas.get_tk_widget().grid(row=0, column=0)
        self.cid = self.canvas.mpl_connect('button_press_event', self.onclick)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.tbframe)
        self.toolbar.update()

        self.listframe = tk.LabelFrame(self.top_frame, padx=20, pady=16)
        self.listframe.grid(row=1, column=1)
        self.spectralist = tk.Listbox( self.listframe, height=plot_height * 10, font=( "Helvetica", 12))
        self.spectralist.pack(side="left", fill="x")
        self.scrollbar = tk.Scrollbar(self.listframe, orient="vertical")
        self.scrollbar.config(command=self.spectralist.yview)
        self.scrollbar.pack(side="left", fill="y")
        # self.populate_list()
        self.spectralist.bind('<Double-1>', self.on_list_select)

        ####

        self.commandframe = tk.LabelFrame(self.top_frame, padx=15, pady=15)
        self.commandframe.grid(row=2, column=0)

       # Plot
        self.pbutton = tk.Button( self.commandframe, text="Show", command=lambda: self.plot_spectra(), \
                                 padx=10, pady=4, font=( "Helvetica", 16))
        self.pbutton.grid(row=0, column=1)
        self.orig_pcolor = self.pbutton.cget("background")
        # self.pbutton['state'] = tk.DISABLED

       # Calibrate
        self.cbutton = tk.Button( self.commandframe, text="Calibrate", command=self.calibrate_sp,\
                                  padx=10, pady=4, font=( "Helvetica", 16))
        self.cbutton.grid(row=0, column=2)

        self.hscale_var = tk.DoubleVar()
        self.hscale_var.set(50)
        self.hscaler = tk.Scale( self.plotframe, from_=1, to=100, command=self.scaleSpectra, \
                                variable=self.hscale_var, orient=tk.HORIZONTAL, length=300)
        self.hscaler.grid(row=1, column=0)

        self.sbutton = tk.Button( self.commandframe, text="Save", command=self.save_adjusted_sp, padx=5, pady=4, font=( "Helvetica", 16))
        self.sbutton.grid(row=0, column=3)

       # Quit
        self.qbutton = tk.Button( self.commandframe, text="Quit", command=self.quit, padx=5, pady=4, font=( "Helvetica", 16))
        self.qbutton.grid(row=0, column=4)
        # Progress
        self.settingframe = tk.LabelFrame(self.commandframe, padx=5, pady=5)
        self.settingframe.grid(row=0, column=5)
        self.peakframe = tk.LabelFrame(self.settingframe, padx=5, pady=5)
        self.peakframe.grid(row=0, column=0)
        self.peakbutton = tk.Button( self.peakframe, text="Peaks", command=self.find_peaks,\
                                     padx=5, pady=4, font=( "Helvetica", 16))
        self.peakbutton.grid(row=0, column=0)
        self.checkvar3 = tk.IntVar()
        self.checkvar3.set(0)
        self.picks_max = tk.Checkbutton( self.peakframe, text='Detect maximas   ', \
                                        variable=self.checkvar3, onvalue=1, offvalue=0, command=self.peak_mode)
        self.picks_max.grid(row=0, column = 1)

        self.baselineframe = tk.LabelFrame(self.settingframe, padx=5, pady=5)
        self.baselineframe.grid(row=1, column=0)
        self.sbutton = tk.Button( self.baselineframe, text="Baseline",\
                                  command=self.detect_baseline, padx=5, pady=4, font=( "Helvetica", 16))
        self.sbutton.grid(row=0, column=0)
        self.checkvar1 = tk.IntVar()
        self.poly_checkbtn = tk.Radiobutton( self.baselineframe, text='Poly', variable=self.checkvar1, value=1)
        self.checkvar1.set(0)
        self.poly_checkbtn.grid(row=0, column=1)
        self.morpth_checkbtn = tk.Radiobutton( self.baselineframe, text='Morph', variable=self.checkvar1, value=0)
        self.morpth_checkbtn.grid(row=0, column=2)
        self.top_frame.pack()
        # self.span_select = SpanSelector( self.mwax, self.on_pltselect, 'horizontal', useblit=True, rectprops=dict( alpha=0.5, facecolor='red'), button=3)

    def quit(self):
        self.parent.quit()     # stops mainloop
        self.parent.destroy()  # this is necessary on Windows to prevent crash

    def calibrate_sp(self):
        #try:
        cl_fname = '{}_{}'.format( self.sp_range[0], self.sp_range[1]) + '_cal_lines.dat' 
        cl_path = os.path.join(self.savepath, cl_fname)
        
        if self.peak_is_found == True:
            self.cal_wv = self.ax1_lines 
            self.cal_pix = self.ax2_lines
        print(self.cal_pix)
        with open(cl_path, 'w') as f:
            if len(self.cal_wv) == len(self.cal_pix) and len(self.cal_pix) > 0:

                for i, j in zip(self.cal_wv, self.cal_pix):
                    f.write('%4.2f %4.1f\n' % (i, j))
                #self.calibrator = Calibrator(self.savepath, self.spectrum, cl_fname)
                self.spectrum = (self.spectrum - np.min(self.morph_baseline)) / (np.max(self.morph_baseline)\
                                                                                  - np.min(self.morph_baseline))
                self.calibrator = Calibrator(self.savepath, self.spectrum, self.cal_wv, self.cal_pix)
                self.spec= self.calibrator.y2
                self.spectra= self.calibrator.y2
                #self.spec= self.calibrator.y2
                #self.spectra = self.spec
                self.wavelength  = self.calibrator.xcal
                print(self.spectra)
                self.ax.clear()
                self.threadnm = "cali"
                self.plot_spectra()
            else:
                showerror(title='Error',message= f'Calibration data must be non empty and the same size \
                          Sim={len(self.cal_wv)} Dig={len(self.cal_pix)}\
                          Try middle click to delete picks')
#        except:
#            self.pbutton.config(bg="light blue")


        # self.threadnm = "digi"

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

        jsparser = JsonParser(self.savepath, [])
        try:
            self.data = jsparser.read_json('spectra_file.json')
        except FileNotFoundError:
            self.data = []
        if self.threadnm == "cali":
            self.spectralist.delete(0, tk.END)
            self.cbutton['state'] = tk.DISABLED
            for dx in self.data:
                self.spectralist.insert(tk.END, dx.calsp_name)
            self.ax.clear()
            self.canvas.draw()

        if self.threadnm == "digi":
            self.spectralist.delete(0, tk.END)
            for dx in self.data:
                self.spectralist.insert(tk.END, dx.img_name)

    def on_list_select(self, event):

        self.active = self.spectralist.get(tk.ACTIVE)
        self.threadnm = "digi"
        if self.data:
            for od in self.data:
                if self.active == od.calsp_name and self.threadnm == "cali":
                    self.sp_selected = od.calsp_name
                    print(self.sp_selected)
                    self.sp_range = od.sp_range
                    print(self.sp_range)
                if self.active == od.img_name and self.threadnm == "digi":
                    self.sp_digi = od.sp_name
                    self.sp_range = od.sp_range
            if self.threadnm == "cali":
                self.pbutton['state'] = "normal"

                self.ax.clear()
                self.mwax.clear()
                self.calax.clear()
                self.ax1_lines = []
                self.ax2_lines = []
                self.canvas.draw_idle()
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
            simulated_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),'simulated.npz')
            simulated_data = np.load(simulated_path)
            self.ftir_wv= simulated_data['simulated_wn']
            self.ftir_in= simulated_data['simulated_in']
            self.selectedftir_wv = self.ftir_wv[(self.ftir_wv > ( self.sp_range[0] )) & (self.ftir_wv < (self.sp_range[1] ))]
            self.selectedftir_in = self.ftir_in[(self.ftir_wv < ( self.sp_range[1] )) & (self.ftir_wv > (self.sp_range[0] ))]
            self.savepath = SpectraConfig.read_conf()['spectra.conf']['spectrapath'] 

            self.spectrum = np.loadtxt( os.path.join( self.savepath, self.sp_digi), skiprows=0)
            self.pixel_xvals = np.arange(len(self.spectrum))
    
            self.ax.plot( self.selectedftir_wv, self.selectedftir_in, 'r', linewidth=0.7)
            self.ax.set_ylim(self.mwax.get_ylim()[::-1])
            self.mwaxline, = self.mwax.plot(self.pixel_xvals, self.spectrum, linewidth=0.7)
            self.mwax.set_ylim(self.mwax.get_ylim()[::-1])
            self.ax.invert_yaxis()
            self.mwax.invert_yaxis()
            self.canvas.draw_idle()
        except FileNotFoundError:
            print("File Not found")

    def plot_spectra(self):
        self.ax.clear()
        self.pbutton.config(bg=self.orig_pcolor)
        if self.threadnm == "digi":
            self.populate_list()
        # get selected spectra and plot
        elif self.threadnm == "cali":
            try:
                self.ax.plot( self.selectedftir_wv, self.selectedftir_in, 'r', linewidth=0.7)
                self.axline, = self.ax.plot( self.wavelength, self.spec / np.max(self.spec), linewidth=0.7)
                self.hscaler.configure( from_=np.min( self.wavelength), to=np.max( self.wavelength), resolution=0.01)
                # self.hscaler_p.configure(from_ = self.sp_range[0], to = self.sp_range[1], resolution = 0.01)
                self.mean_wv = (np.min(self.wavelength) +
                                np.max(self.wavelength)) / 2
                self.hscale_var.set(int(self.mean_wv))
                self.calax.plot(self.ax2_lines, self.ax1_lines, '.', picker = 1, markersize = 2)
                # self.hscale_var_p.set(int(self.mean_wv))
                self.canvas.draw()
            except FileNotFoundError:
                print('File not found')

    def detect_baseline(self):
        try:
            baseline_fitter = Baseline(np.arange(len(self.spectrum)))
            if (self.checkvar1.get() == 1):
                self.poly_baseline = baseline_fitter.modpoly(self.spectrum, poly_order=3)[0]
                print(np.min(self.selected_baseline))
            elif (self.checkvar1.get() == 0): 
                self.morph_baseline = baseline_fitter.mor(self.spectrum, half_window=30)[0]
            else:
                pass
            #self.mwax.clear()
            self.mwax.plot(self.morph_baseline, linewidth=0.7)
            self.canvas.draw_idle()
        except AttributeError:
            self.pbutton.config(bg='light blue')

    def peak_mode(self):
        if self.checkvar3.get() == 0:
            print('Mode: detect minimas')
        elif self.checkvar3.get() == 1:
            print('Mode : detect maximas')
        else:
            pass

    def find_peaks(self):

        self.index = 0
        try:
            if self.checkvar3.get() == 0:
                self.digi_peaks, _ = find_peaks((-1)*self.spectrum + np.max(self.spectrum) ,prominence=self.digi_prom)
                self.sim_peaks, _ = find_peaks((-1)*self.selectedftir_in + np.max(self.selectedftir_in), prominence=self.sim_prom)
            elif self.checkvar3.get() == 1:
                self.digi_peaks, _ = find_peaks(self.spectrum, prominence=self.digi_prom)
                self.sim_peaks, _ = find_peaks(self.selectedftir_in, prominence=self.sim_prom)
            self.sim_xpeaks = [self.sim_peaks,self.selectedftir_wv[self.sim_peaks]]
            self.digi_xpeaks = [self.digi_peaks,self.pixel_xvals[self.digi_peaks]]
            self.smax, = self.ax.plot(self.sim_xpeaks[1], self.selectedftir_in[self.sim_peaks], 'x', picker=3, markersize=3)
            self.dgax, = self.mwax.plot(self.digi_xpeaks[1], self.spectrum[self.digi_peaks], 'x', picker=3, markersize=3)
            self.ax1_lines = np.asarray(self.sim_xpeaks[1])
            self.ax2_lines = np.asarray(self.digi_xpeaks[1])
            self.peak_is_found = True
        except AttributeError:
            showerror(title='Error',message= f'Define detection boundary -> Right click')

        self.canvas.draw_idle()

    def show_selected(self):
        try:
            baseline_fitter = Baseline(np.arange(len(self.spectrum)))
            if (self.checkvar1.get() == 1):
                self.selected_baseline = baseline_fitter.modpoly(self.spectrum, poly_order=3)[0]
            elif (self.checkvar1.get() == 0): 
                self.selected_baseline = baseline_fitter.mor(self.spectrum, half_window=30)[0]
            else:
                pass
        except:
            pass


    def onclick(self, event):
        if event.dblclick:
            self.peak_is_found = True
            if event.inaxes == self.ax:
                self.ax1_lines = np.append(self.ax1_lines, event.xdata)
                self.ax1l = self.ax.vlines(self.ax1_lines, 0, 1, linestyle='solid', linewidth=0.5)
                self.canvas.draw_idle()
            elif event.inaxes == self.mwax:
                self.ax2_lines = np.append(self.ax2_lines,event.xdata)
                self.ax2l = self.mwax.vlines( self.ax2_lines, 0, 1, transform=self.mwax.get_xaxis_transform(), linestyles='solid', linewidth=0.5)
                self.canvas.draw_idle()
            else:
                pass
        else:
            if event.button == 3:
                if event.inaxes == self.ax:
                    self.sim_prom = event.ydata
                    self.ay1l = self.ax.axhline(y=self.sim_prom, linestyle='solid', linewidth=0.5)
                    self.canvas.draw_idle()
                elif event.inaxes == self.mwax:
                    self.digi_prom = event.ydata
                    self.ay2l = self.mwax.axhline(y=self.digi_prom, linestyle='solid', linewidth=0.5)
                    self.canvas.draw_idle()

            if event.button == 2:
                if event.inaxes == self.ax:
                    idx_1 = self.find_nearest_peak(self.sim_xpeaks[1], event.xdata)
                    self.sim_xpeaks[0] = np.delete(self.sim_xpeaks[0], idx_1)
                    self.sim_xpeaks[1] = np.delete(self.sim_xpeaks[1], idx_1)
                    self.smax.set_data(self.sim_xpeaks[1], self.selectedftir_in[self.sim_xpeaks[0]])
                    self.canvas.draw_idle()
                    self.ax1_lines = self.sim_xpeaks[1]
                elif event.inaxes == self.mwax:
                    idx_2 = self.find_nearest_peak(self.digi_xpeaks[1], event.xdata)
                    self.digi_xpeaks[0] = np.delete(self.digi_xpeaks[0], idx_2)
                    self.digi_xpeaks[1] = np.delete(self.digi_xpeaks[1], idx_2)
                    self.dgax.set_data(self.digi_xpeaks[1], self.spectrum[self.digi_xpeaks[0]])
                    self.canvas.draw_idle()
                    self.ax2_lines = self.digi_xpeaks[1]
            else:
                pass
    def scaleSpectra(self, dummy):
        if self.threadnm == "cali":
            hscale_value = self.hscaler.get()
            x_vals = self.wavelength * (hscale_value / self.mean_wv) #+ hscale_value_p / self.mean_wv
            self.axline.set_xdata(x_vals)
            self.canvas.draw_idle()
        else:
            print("First plot spectra to scale")

    def find_nearest_peak(self, arr, val):
        arr = np.asarray(arr)
        idx = (np.abs(arr - val)).argmin()
        return idx

    def reduce_points(self, xo, yo,res=0.0258):
        yn = []
        xmin, xmax = np.min(xo), np.max(xo)
        xn = np.linspace(xmin, xmax, int((xmax-xmin)/res))
        for x in xn:
            yn.append(np.median(yo[(xo > x-res/2) & (xo < x+res/2)]))
        return xn, yn

    def save_adjusted_sp(self):
        config = SpectraConfig.read_conf()
        self.sp_date = datetime.datetime.strptime(config['spectra.conf']['Date'], '%d/%m/%Y')
        self.stime = datetime.datetime.strptime(config['spectra.conf']['Starttime'], '%H:%M')
        self.etime = datetime.datetime.strptime(config['spectra.conf']['Endtime'], '%H:%M')

        self.latlon = np.array(config['spectra.conf']['Latitude/Longitude'].split(','), dtype = float)
        self.date_time_obj = (datetime.datetime.combine(self.sp_date.date(),self.stime.time()))\
            .replace(tzinfo=datetime.timezone.utc)- datetime.timedelta(hours=1)
        self.sza = float(90) - get_altitude(float(self.latlon[0]), float(self.latlon[1]), self.date_time_obj)
        self.print_sfit_readable_spectrum(float(self.sza), self.latlon, self.date_time_obj)

    def print_sfit_readable_spectrum(self, sza=63.0, latlon=(46.55, 7.98), d=datetime.datetime(1951, 4, 15, 7, 30, 0),\
                                     res=0.25, apo='TRI', sn=100.0, rearth=6377.9857):
        try:    
            new_line = np.hstack(self.axline.get_xdata())
            spc = np.hstack(self.spectra)
            new_line, spc = self.reduce_points(new_line, spc)
            wvn_bounds = [np.min(new_line), np.max(new_line)]
            dt_str = d.strftime('%d%m%Y%H%M%S')
            #fname = os.path.join(self.savepath, '{:.2f}_{:.2f}_calibrated.dat'.format(wvn_bounds[0],wvn_bounds[1]))
            fname = os.path.join(self.savepath, 'jfj_{}_calibrated.dat'.format(dt_str))
            #pdb.set_trace()
            s = ' %4.2f  %8.4f  %4.2f  %5.2f  %5i\n'%(sza, rearth, latlon[0], latlon[1] , sn)
            s = s + d.strftime(' %Y %m %d %H %M %S\n')
            s = s + d.strftime(' %d/%m/%Y, %H:%M:%S')+', RES=%5.4f  APOD FN = %3s\n'%(res, apo)
            s = s + ' %7.3f %7.3f %11.10f %7i'%(wvn_bounds[0], wvn_bounds[1], (wvn_bounds[1]-wvn_bounds[0])/float(len(spc)), len(spc))
            for i in spc:
                s+='\n %8.5f'%(i)
                with open(fname, 'w') as f:
                    f.write(s)
            showinfo(title='Saved', message= f'Successfully saved {fname}')
            np.save('Calibrated', [new_line, spc])
            np.save('Simulated', [self.selectedftir_wv,self.selectedftir_in])
        except:
            showerror(title='Save Error', message='Can\'t save file')

if __name__ == "__main__":
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.resizable(False, False)
    root.title("Spectra Digitizer")
    root.geometry("{}x{}".format(
        int(width - 0.2 * width), int(height - 0.2 * height)))
    CaliApp(root).pack()
    root.mainloop()
