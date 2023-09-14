#!/usr/bin/python3
from __future__ import print_function, division
import concurrent.futures
import os
from utilfunc import create_sprange
import numpy as np
import cv2
import scipy.interpolate as intp
from config import SpectraConfig
from spectrum import Spectrum
from jsonparser import JsonParser
from glob import glob
import datetime

class Digitizer():

    def __init__(self, dpath, savepath):
        self.digitized_spectrum = []

        self.dpath = dpath
        self.sp_range = []
        self.savepath = savepath
        self.parallelize()

    def parallelize(self):
        self.img_names =  sorted(glob(os.path.join(self.dpath,'*.tif')))
        self.img_shapes = [cv2.imread(img_path).shape for img_path in self.img_names]
        min_wavelength = float(SpectraConfig.read_conf()['spectra.conf']['minwavelength'])
        max_wavelength = float(SpectraConfig.read_conf()['spectra.conf']['maxwavelength'])
        self.sp_range = create_sprange(min_wavelength, max_wavelength, len(self.img_names))
        print(self.img_names)

        self.spectrums = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
            for spectrum in executor.map(
                    self.digitize_spectrum, self.img_names, self.img_shapes, self.sp_range
                    ):
                self.spectrums.append(spectrum)
        json_parser = JsonParser('data' ,self.spectrums)
        json_parser.save_json()

    def digitize_spectrum(self,img_fname, im_shape, sp_range):
        img1 = cv2.imread(os.path.join(img_fname))
        hsv = cv2.cvtColor(img1,cv2.COLOR_BGR2HSV)

        #min_val = np.array([0,100,100])
        min_val = np.array([0,100,100])
        max_val = np.array([10,255,255])
        mask = cv2.inRange(hsv, min_val, max_val)
        result = cv2.bitwise_and(img1,img1, mask= mask)
        grayImage = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        grayImageF = cv2.GaussianBlur(grayImage,(13,13),0) #remove salt and peper noise
        (_, source) = cv2.threshold(grayImageF, 27, 255, cv2.THRESH_BINARY)
        sp_pixels = np.arange(source.shape[0])
        spectrum = np.array([np.mean(sp_pixels[np.flip(bw)]) for bw in (source.T == 0xFF)])
        idx = np.arange(spectrum.shape[0])
        nanind = np.where(np.isfinite(spectrum))
        inp = intp.interp1d(idx[nanind], spectrum[nanind],bounds_error=False)
        self.digitized_spectrum = np.where(np.isfinite(spectrum),spectrum,inp(idx)) #interpolate mising data
        self.digitized_spectrum = self.digitized_spectrum[np.logical_not(np.isnan(self.digitized_spectrum))]
        impath = img_fname

        #sp_name = img_fname[:-4] + '_digitized'+'.dat'
        config = SpectraConfig.read_conf()
        self.sp_date = datetime.datetime.strptime(config['spectra.conf']['Date'], '%d/%m/%Y')
        self.stime = datetime.datetime.strptime(config['spectra.conf']['Starttime'], '%H:%M')
        combined_dt = (datetime.datetime.combine(self.sp_date.date(),self.stime.time()))\
            .replace(tzinfo=datetime.timezone.utc)- datetime.timedelta(hours=1)
        dt_str = combined_dt.strftime('%d%m%Y%H%M%S')
        spath =f"jfj_{dt_str}_digitized.dat"
        #spath = sp_name
        with open(os.path.join(spath), 'w') as f:
            for i in self.digitized_spectrum:
                f.write('%6.2f\n'%i)
        print('{}'.format(spath))
        return  Spectrum(impath,im_shape,spath, sp_range = sp_range )
