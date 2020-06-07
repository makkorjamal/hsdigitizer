# import image_slicer
from image_slicer import slice
from sklearn.impute import SimpleImputer
import numpy as np
import os
import glob

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

