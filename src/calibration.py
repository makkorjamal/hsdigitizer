#!/usr/bin/python3
from __future__ import print_function, division
import os, pickle, sys
from config import SpectraConfig
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, TextBox
from scipy.optimize import curve_fit
import pdb
import datetime
from pysolar.solar import *


class Calibrator():

    
    def read_cali_lines(self):
        fname = os.path.join(self.savepath, self.cal_name)
        with open(fname, 'r') as f:
            ll = f.readlines()
        self.ax1_lines = [float(i.split()[0]) for i in ll]
        self.ax2_lines = [float(i.split()[1]) for i in ll]
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
        self.sp_digitized = self.sp_digitized*(-1)+np.max(self.sp_digitized)
        self.cal_name = cal_name
        self.yoffset = 0
        self.y2 = (self.sp_digitized-self.yoffset)/np.max(self.sp_digitized-self.yoffset)
        self.x2 = np.arange(len(self.y2))
        #
        self.ax1_lines, self.ax2_lines = [], []
        self.read_cali_lines()
        self.reduce_points()
