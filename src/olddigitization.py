#!/usr/bin/python3
#By Matthias Buschmann
from __future__ import print_function, division
import warnings
import concurrent.futures
import os
from utilfunc import create_sprange
import numpy as np
import cv2
from config import SpectraConfig
from spectrum import Spectrum
from jsonparser import JsonParser
from glob import glob

class Digitizer():

    def __init__(self, dpath, savepath):
        self.digitized_spectrum = []

        self.dpath = dpath
        self.sp_range = []
        self.savepath = savepath
        self.parallelize()

    def parallelize(self):
        self.img_names =  sorted(glob(os.path.join(self.dpath,'*.tif')))
        min_wavelength = float(SpectraConfig.read_conf()['spectra.conf']['minwavelength'])
        max_wavelength = float(SpectraConfig.read_conf()['spectra.conf']['maxwavelength'])
        self.sp_range = create_sprange(min_wavelength, max_wavelength, len(self.img_names))
        print(self.img_names)

        self.spectrums = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
            for spectrum in executor.map(
                    self.digitize_spectrum, self.img_names, self.sp_range
                    ):
                self.spectrums.append(spectrum)
        json_parser = JsonParser('data' ,self.spectrums)
        json_parser.save_json()

    def digitize_spectrum(self,img_fname, sp_range):

        img = cv2.imread(os.path.join(self.dpath, img_fname))
        self.img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.b, self.g, self.r = cv2.split(self.img)
        for i in range(self.img.shape[1]):
            self.digitized_spectrum.append(self.digitize_point(i))
        if self.digitized_spectrum:
            self.digitized_spectrum = np.asarray(self.digitized_spectrum)*(-1) + np.max(self.digitized_spectrum)
            print(self.digitized_spectrum)
            impath = img_fname
            sp_name = img_fname[:-4] + '_digitized'+'.dat'
            spath = sp_name
            with open(os.path.join(spath), 'w') as f:
                for i in self.digitized_spectrum:
                    f.write('%4.2f\n'%i)
            print('{}'.format(spath))
            return  Spectrum(impath,sp_name, sp_range = sp_range )

    def digitize_point(self, s):
        x = np.arange(self.img.shape[0])
        y = np.divide(self.b[:, s],self.g[:, s],where = self.g[:,s] != 0)
        cond = (y>(np.max(y))*0.84)# 
        
        with warnings.catch_warnings():

            warnings.filterwarnings('error')
            try:
                return np.nanmean(x[cond])
            except RuntimeWarning:
                return np.NaN
