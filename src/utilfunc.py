import image_slicer
from sklearn.impute import SimpleImputer
import numpy as np

def imputate_nan(sp_file):
    idx1 = np.arange(0, 70)
    idx2 = np.arange(10130, len(sp_file))
    index = idx1.concat(idx2)
    print(index)
    # imp = SimpleImputer(missing_values=np.nan, strategy='mean')
    # imp.fit([[1, 2], [np.nan, 3], [7, 6]])
    # SimpleImputer()
    # X = [[np.nan, 2], [6, np.nan], [7, 6]]
    # print(imp.transform(X))

