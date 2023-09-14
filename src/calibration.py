from lmfit import Model
import numpy as np
from tqdm import tqdm
from lmfit import Model
from tqdm import tqdm
import numpy as np

class Calibrator():

    def __init__(self, savepath, sp_digitized):
        self.savepath = savepath
        self.sp_digitized = sp_digitized
        self.yoffset = 0
        self.y2 = (self.sp_digitized - self.yoffset) / np.max(self.sp_digitized - self.yoffset)
        self.x2 = np.arange(len(self.y2))
        self.read_cali_lines()

    def read_cali_lines(self):
        self.cal_wv, self.cal_pix = np.genfromtxt(self.savepath, delimiter=' ', unpack=True)
        self.calibrate()

    def calibrate(self):
        # Define the polynomial model 
        def n_polynomial(x, a, b, c, d):
            return a * x**3 + b * x**2 + c * x + d
        model = Model(n_polynomial)
        params = model.make_params(a=0, b=0, c=0, d=0)
        pbar = tqdm(total=100, desc="Fitting Progress")
        def update_progress(params, iter, resid, *args, **kws):
            pbar.update(1)
        result = model.fit(self.cal_wv, x=self.cal_pix, params=params, iter_cb=update_progress)
        self.xcal = result.eval(x=self.x2)
        pbar.close()
        with open('fit.stats', 'a') as f:
            for line in result.fit_report():
                f.write(line)
