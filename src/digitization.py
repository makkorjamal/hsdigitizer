#!/usr/bin/python3
from __future__ import print_function, division
import warnings
import concurrent.futures
import math
import matplotlib
import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
from spectrum import Spectrum
from jsonparser import JsonParser
import glob

class Digitizer():

    def __init__(self, dpath, savepath):
        self.digitized_spectrum = []

        self.dpath = dpath
        self.sp_range = []
        self.savepath = savepath
        self.parallelize()

    def parallelize(self):
        # self.img_names = sorted(glob.glob(os.path.join(self.dpath,'*.tif')))
        self.img_names = sorted(os.listdir(self.dpath))
        print(self.img_names)

        self.spectrums = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
            for spectrum in executor.map(
                    self.digitize_spectrum, self.img_names
                    ):
                self.spectrums.append(spectrum)
        json_parser = JsonParser('data' ,self.spectrums)
        json_parser.save_json()

    def digitize_spectrum(self,img_fname):

        # self.img = cv2.imread(os.path.join(self.dpath, img_fname))
        img = cv2.imread(os.path.join(self.dpath, img_fname))
        self.img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.b, self.g, _ = cv2.split(self.img)
        # self.digitized_spectrum = np.array([])
        for i in range(self.img.shape[1]):
            self.digitized_spectrum.append(self.digitize_point(i))

        if self.digitized_spectrum:
            impath = img_fname
            sp_name = img_fname[:-4]+'_digitized'+'.dat'
            spath = os.path.join(self.savepath,sp_name)
            with open(spath,'w') as f:
                for i in self.digitized_spectrum:
                    f.write('%4.2f\n'%i)
            print('{}'.format(spath))
            return  Spectrum(impath,sp_name, sp_range = self.sp_range)

    def digitize_point(self, s):
        x = np.arange(self.img.shape[0])
        y = np.divide(self.b[:, s],self.g[:, s],where = self.g[:,s] != 0)
        cond = (y>(np.max(y))*0.80) & (y<(np.max(y))*0.99)
        
        with warnings.catch_warnings():

            warnings.filterwarnings('error')
            try:
                return np.nanmean(x[cond])
            except RuntimeWarning:
                return np.NaN

if __name__ == '__main__':
    # dpath = 'images/'
    savepath = 'data/'
    dpath = '/mnt/740617C970FA5889/scroll1_21_aout/'
    # dpath = '/home/jamal/spectra'
    Digitizer(dpath, savepath)




