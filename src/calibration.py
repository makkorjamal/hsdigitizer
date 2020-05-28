#!/usr/bin/python3
from __future__ import print_function, division
import os
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, TextBox
from scipy.optimize import curve_fit
from jsonparser import JsonParser
import concurrent.futures
from spectrum import Spectrum
from itertools import zip_longest


class Calibrator():

    def parallelize(self):
        jsparser = JsonParser(self.savepath,[])
        self.data = jsparser.read_json('spectra_file.json')
        self.spectrums = []
        tmp_img_names = []
        tmp_sp_names = []
        tmp_sp_ranges = []
        tmp_calsp_names = []
        tmp_calsplines_names = [] 


        sp_names = []
        for dd in self.data:
            tmp_img_names.append(dd.img_name)
            tmp_sp_names.append(dd.sp_name)
            tmp_sp_ranges.append(dd.sp_range)

        with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
            for names in executor.map(self.save_data,tmp_sp_names): 
                tmp_calsplines_names.append(names[1])
                tmp_calsp_names.append(names[0])
        self.spectrums = [Spectrum(tmp_img_name, tmp_sp_name, tmp_calsp_name, tmp_calsplines_name, tmp_sp_range) for tmp_img_name, tmp_sp_name, tmp_calsp_name, tmp_calsplines_name , tmp_sp_range in zip_longest(tmp_img_names, tmp_sp_names, tmp_calsp_names, tmp_calsplines_names, tmp_sp_ranges)]
        json_parser = JsonParser(self.savepath,self.spectrums)
        json_parser.save_json()

    def save_data(self,digitized_sp):
        self.fname = digitized_sp
        # print('Reading ', os.path.join(self.path, self.fname), '...')
        self.data = np.recfromtxt(os.path.join(self.path, self.fname), names=['y'], skip_header=0, encoding='utf8')
        self.y = self.data.y*(-1)+np.max(self.data.y)
        self.yoffset = 0
        self.y2 =( self.y-self.yoffset)/np.max(self.y-self.yoffset)
        self.x2 = np.arange(len(self.y2))
        # print('Setting initial spectral range to: ', self.s, '--', self.e, '...')
        #
        self.ax1_lines, self.ax2_lines = [], []
        self.read_cali_lines()
        self.reduce_points(None)
        return self.print_sfit_readable_spectrum(None)

    def print_sfit_readable_spectrum(self,event, sza=63.0, latlon=(46.55, 7.98), d=dt.datetime(1951, 4, 15, 7, 30, 0), res=0.25, apo='TRI', sn=100.0, rearth=6377.9857):
        spc = self.yreduced
        wvn_bounds = [np.min(self.xcal), np.max(self.xcal)]
        cl_fname = os.path.join(self.path, self.fname[:-4]+'_cal_lines.dat')
        with open(cl_fname, 'w') as f:
            for i, j in zip(self.ax1_lines, self.ax2_lines):
                f.write('%4.4f %4.4f\n'%(i,j))
        # print('Wrote file', cl_fname)
        c_fname = os.path.join(self.path, self.fname[:-4].replace("_digitized", "")+'_calibrated.dat')
        #pdb.set_trace()
        s = ' %4.2f  %8.4f  %4.2f  %5.2f  %5i\n'%(sza, rearth, latlon[0], latlon[1] , sn)
        s = s + d.strftime(' %Y %m %d %H %M %S\n')
        s = s + d.strftime(' %d/%m/%Y, %H:%M:%S')+', RES=%5.4f  APOD FN = %3s\n'%(res, apo)
        s = s + ' %7.3f %7.3f %11.10f %7i'%(wvn_bounds[0], wvn_bounds[1], (wvn_bounds[1]-wvn_bounds[0])/float(len(spc)), len(spc))
        for i in spc:
            s+='\n %8.5f'%(i)
        with open(c_fname, 'w') as f:
            f.write(s)
        # print('Wrote file', c_fname)
        return [c_fname.replace(self.savepath, ""), cl_fname.replace(self.savepath,"")]
    
    def read_cali_lines(self):
        fname = os.path.join(self.path, '13490167_digitized_cal_lines.dat')
        with open(fname, 'r') as f:
            ll = f.readlines()
        self.ax1_lines = [float(i.split()[0]) for i in ll]
        self.ax2_lines = [float(i.split()[1]) for i in ll]
        # print(self.ax1_lines)
        # print(self.ax2_lines)
        # print('Read calibration lines from', fname)
        self.calibrate(None)
    
    def reduce_points(self, event, res=0.05):

        xo = self.xcal
        yo = self.y2
        yn = []
        xmin, xmax = np.min(self.xcal), np.max(self.xcal)
        xn = np.linspace(xmin, xmax, int((xmax-xmin)/res))
        for x in xn:
            yn.append(np.median(yo[(xo > x-res/2) & (xo < x+res/2)]))
        self.yreduced = np.array(yn)
        self.xreduced = xn
        # self.ax1.plot(self.xreduced, self.yreduced, '-')
        # self.fig.canvas.draw_idle()

        
    def calibrate(self, event):
        l1 = np.unique(np.array(self.ax1_lines))
        l2 = np.unique(np.array(self.ax2_lines))
        l1.sort()
        l2.sort()
        f = lambda x, a,b: a*x+b
        p, pcov = curve_fit(f, l2, l1)
        #print(p)
        #pdb.set_trace()
        # valid = ~(np.isnan(self.x2))
        self.xcal = f(self.x2, *p)

    def __init__(self, dpath, savepath):
        self.path = dpath
        self.savepath = savepath
        self.parallelize()
        # d = np.recfromtxt('data/S16428AC_025_trian_zf2.dpt', names=['w', 'i'], encoding='utf8')
        # self.x1 = d.w
        # self.y1 = d.i


if __name__ == '__main__':
    #if len(sys.argv)==2:
    path = 'data/'
    # fname = 'digitized_copyscan_2901_2926_a.dat'#sys.argv[1]
    fname = 'digitized_14065069.dat'#sys.argv[1]
    Calibrator(path, path)
