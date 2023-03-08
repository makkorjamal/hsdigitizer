#!/usr/bin/python3
from __future__ import print_function, division
import os
from numpy import genfromtxt, unique, polyfit, poly1d, arange, max

class Calibrator():

    
    def read_cali_lines(self):
        print(self.savepath)
        #print(self.ax2_lines)
        print('Read calibration lines from', self.savepath)
        #print(f"the length before calibration {len(self.ax1_lines)} {len(self.ax2_lines)}")
        self.calibrate(None)

    def calibrate(self, event):
        #self.read_cali_lines()
        l1 = unique(self.ax1_lines)
        l2 = unique(self.ax2_lines)
        l1.sort()
        l2.sort()
        z = polyfit(l2,l1, 3)
        p = poly1d(z)
        self.xcal = p(self.x2)

    def __init__(self, savepath, sp_digitized, ax1_lines, ax2_lines):
        self.savepath = savepath
        self.sp_digitized = sp_digitized
        self.yoffset = 0
        self.y2 = (self.sp_digitized-self.yoffset)/max(self.sp_digitized-self.yoffset)
        self.x2 = arange(len(self.y2))
        #
        print(ax1_lines)
        self.ax1_lines, self.ax2_lines = ax1_lines, ax2_lines
        print(self.ax1_lines)
        self.calibrate(None)