# import image_slicer
from vassal.terminal import Terminal
import image_slicer 
from sklearn.impute import SimpleImputer
import numpy as np
import os
from itertools import product

import glob

def read_spectra(filename):
    # file = np.genfromtxt(filename)
    with open(filename) as f:
        lines = f.readlines()
        print(lines[0])
    sec_line = np.fromstring(lines[1], dtype = np.float16, sep = '\t')
    sec_line = sec_line.astype(np.float)
    spec = np.array(lines[2:])
    spec = spec.astype(np.float)

    wavelength = np.linspace(sec_line[0], sec_line[1], int(sec_line[3]))
    datafile = os.path.join('data/', 'simulated.dat')
    with open(datafile, 'w+') as datafile_id:
        np.savetxt(datafile_id,list(zip(wavelength,spec)))
    
def create_sprange(sp_min, sp_max,nm_sp):
    c = []
    ra = np.linspace(sp_min, sp_max, nm_sp + 1)
    ra = [int(i) for i in ra]
    [c.append([ra[i-1],ra[i]] ) for i in np.arange(1, len(ra))]
    return c

def imputate_nan(sp_file):
    idx1 = np.arange(0, 70)
    idx2 = np.arange(10129, len(sp_file))
    index = np.concatenate(( idx1, idx2 ))
    newfile = np.delete(sp_file, index)
    newfile = newfile.reshape(1,-1)
    imp = SimpleImputer(missing_values=np.nan, strategy='mean')
    imp.fit(newfile)
    imputated_file = imp.transform(newfile)
    return (imputated_file.flatten())
if __name__=="__main__":
    image_slicer.slice( "images/sroll_17_avril.tif", col=6, row=1, save=True, DecompressionBombWarning=False)
    
