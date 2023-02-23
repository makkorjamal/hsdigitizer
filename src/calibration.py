#!/usr/bin/python3
from __future__ import print_function, division
import os
import numpy as np
from scipy.optimize import curve_fit
from pysolar.solar import *

class Calibrator():

    
    def read_cali_lines(self):
        fname = os.path.join(self.savepath, self.cal_name)
        print(fname)
        with open(fname, 'r') as f:
            ll = f.readlines()
            for line in ll:
                p = line.split()
                self.ax1_lines.append(p[0])
                self.ax2_lines.append(p[1])
        self.ax1_lines = np.asarray(self.ax1_lines, dtype=float)
        self.ax2_lines = np.asarray(self.ax2_lines, dtype=float)
        
        print('Read calibration lines from', fname)
        print(f"the length before calibration {len(self.ax1_lines)} {len(self.ax2_lines)}")
        self.calibrate(None)

    def calibrate(self, event):
        l1 = np.unique(self.ax1_lines)
        l2 = np.unique(self.ax2_lines)
        l1.sort()
        l2.sort()
        z = np.polyfit(l2,l1, 3)
        p = np.poly1d(z)
        self.xcal = p(self.x2)
        #f = lambda x, a,b,c: a*x*x*x +b*x + c
        #p, pcov= curve_fit(f, l2, l1)
        #self.xcal = f(self.x2, *p)

    def __init__(self, savepath, sp_digitized, ax1_lines, ax2_lines):
        self.savepath = savepath
        self.sp_digitized = sp_digitized
        self.cal_name = ''
        self.yoffset = 0
        self.y2 = (self.sp_digitized-self.yoffset)/np.max(self.sp_digitized-self.yoffset)
        self.x2 = np.arange(len(self.y2))
        #
        self.ax1_lines, self.ax2_lines = ax1_lines, ax2_lines
        self.calibrate(None)