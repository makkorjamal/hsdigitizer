# import image_slicer
import image_slicer 
from sklearn.impute import SimpleImputer
import numpy as np
import os
from itertools import product

import glob

def read_spectra(filename, sp_range = []):
    file = np.loadtxt(filename, skiprows = 2)
    wavelength = np.linspace(3200, 3599, len(file))
    spectra = np.array([wavelength, file])
    spectra = spectra.T
    datafile = os.path.join('data/', 'simulated.dat')
    with open(datafile, 'w+') as datafile_id:
        np.savetxt(datafile_id, spectra )
    return spectra
    
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


if __name__ == "__main__":
    print(read_spectra(os.path.join('data/','all.dat')))
    # image_slicer.slice(os.path.join('images/','sroll_17_avril.tif' ), row = 1, col = 6, save = True , DecompressionBombWarning=False)
    # print(create_sprange(3249, 3565, 7))

