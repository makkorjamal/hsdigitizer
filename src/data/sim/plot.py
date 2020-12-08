import glob
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
fileslist = sorted(glob.glob('*.dat'))
data = np.genfromtxt('full_simulated.dat',names = ['wl', 'sp'])
wavelength = data['wl']
spectra = data['sp']

fig, ax = plt.subplots()
fig1, ax1 = plt.subplots()
ax.plot(wavelength, spectra)
# ax1.plot(np.arange(len(autocorr)), autocorr)
plt.show()
