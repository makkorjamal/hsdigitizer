#!/usr/bin/python3
from __future__ import print_function, division
import os, pickle, sys
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, TextBox
from scipy.optimize import curve_fit
import pdb


class Calibrator():

    def print_sfit_readable_spectrum(self, sza=63.0, latlon=(46.55, 7.98), d=dt.datetime(1951, 4, 15, 7, 30, 0), res=0.25, apo='TRI', sn=100.0, rearth=6377.9857):
        spc = self.yreduced
        wvn_bounds = [np.min(self.xcal), np.max(self.xcal)]
        fname = os.path.join(self.savepath, self.cal_name.replace('cal_lines.dat', 'calibrated.dat'))
        #pdb.set_trace()
        s = ' %4.2f  %8.4f  %4.2f  %5.2f  %5i\n'%(sza, rearth, latlon[0], latlon[1] , sn)
        s = s + d.strftime(' %Y %m %d %H %M %S\n')
        s = s + d.strftime(' %d/%m/%Y, %H:%M:%S')+', RES=%5.4f  APOD FN = %3s\n'%(res, apo)
        s = s + ' %7.3f %7.3f %11.10f %7i'%(wvn_bounds[0], wvn_bounds[1], (wvn_bounds[1]-wvn_bounds[0])/float(len(spc)), len(spc))
        for i in spc:
            s+='\n %8.5f'%(i)
        with open(fname, 'w') as f:
            f.write(s)
        print('Wrote file', fname)
    
    def read_cali_lines(self):
        fname = os.path.join(self.savepath, self.cal_name)
        with open(fname, 'r') as f:
            ll = f.readlines()
        self.ax1_lines = [float(i.split()[0]) for i in ll]
        self.ax2_lines = [float(i.split()[1]) for i in ll]
        print(self.ax1_lines)
        print(self.ax2_lines)
        print('Read calibration lines from', fname)
        self.calibrate(None)
    
    def reduce_points(self, res=0.05):

        xo = self.xcal
        yo = self.y2
        yn = []
        xmin, xmax = np.min(self.xcal), np.max(self.xcal)
        xn = np.linspace(xmin, xmax, int((xmax-xmin)/res))
        for x in xn:
            yn.append(np.median(yo[(xo > x-res/2) & (xo < x+res/2)]))
        self.yreduced = np.array(yn)
        self.xreduced = xn

    def calibrate(self, event):
        l1 = np.unique(np.array(self.ax1_lines))
        l2 = np.unique(np.array(self.ax2_lines))
        l1.sort()
        l2.sort()
        f = lambda x, a,b: a*x+b
        p, pcov = curve_fit(f, l2, l1)
        self.xcal = f(self.x2, *p)

    def __init__(self, savepath, sp_digitized, cal_name):
        self.savepath = savepath
        self.sp_digitized = sp_digitized
        self.cal_name = cal_name
        # self.data = np.recfromtxt(os.path.join(self.path, self.fname), names=['y'], skip_header=0, encoding='utf8')
        # self.y = self.data.y*(-1)+np.max(self.data.y)
        self.yoffset = 0
        self.y2 = (self.sp_digitized-self.yoffset)/np.max(self.sp_digitized-self.yoffset)
        self.x2 = np.arange(len(self.y2))
        #
        self.ax1_lines, self.ax2_lines = [], []
        self.read_cali_lines()
        self.reduce_points()
        self.print_sfit_readable_spectrum()
if __name__ == '__main__':
    #if len(sys.argv)==2:
    fname = '/home/jamal/venvs/hsdigitizer/src/data/sroll_17_avril_02_digitized.dat'#sys.argv[1]
    path = 'data/'
    Calibrator(path, fname)
    #else:
        #print('Add image filename as cmdline arg ....')




