#4500 import image_slicer
import pytz
import matplotlib.pyplot as plt
import glob
import image_slicer 
from sklearn.impute import SimpleImputer
from scipy.signal import savgol_filter, fftconvolve, correlate
from pysolar.solar import *
from datetime import datetime, timezone, timedelta
import numpy as np
import os
from itertools import product
from scipy import signal
import glob

def read_spectra(filename, save = False):
    # file = np.genfromtxt(filename)
    with open(filename) as f:
        lines = f.readlines()
    sec_line = np.fromstring(lines[1], dtype = np.float16, sep = '\t')
    sec_line = sec_line.astype(np.float)
    spec = np.array(lines[2:])
    spec = spec.astype(np.float)

    wavelength = np.linspace(sec_line[0], sec_line[1], int(sec_line[3]))
    datafile = os.path.join('data/', 'simulated.dat')
    if save:
        with open(datafile, 'w+') as datafile_id:
            np.savetxt(datafile_id,list(zip(wavelength,spec)))
    else:
        return wavelength, spec

def fileList(source):
    matches = []
    for root, dirnames, filenames in os.walk(source):
        for filename in filenames:
            if filename.endswith('.final'):
                matches.append(os.path.join(root, filename))
    return matches    
# def update_cal_spec(savepath,name, new_wl):
    
#     with open(os.path.join(savepath, name)) as f:
#         lines = f.readlines()
#     wl_line = np.fromstring(lines[3], dtype = np.float16, sep = '\t')
#     lines[3][0].replace(lines[3][0], str(new_wl[0]) )
#     lines[3][1].replace(lines[3][1], str(new_wl[1]) )
#     print(new_wl)
#     new_sp_file = os.path.join(savepath, name)
#     with open(new_sp_file, 'w+') as cal_fil_id(lines):
#         print("wrote new file")


def read_cal_spec(path):

    with open(os.path.join(path)) as f:
        lines = f.readlines()
    wl_line = np.fromstring(lines[3], dtype = np.float16, sep = '\t')
    wl_line = wl_line.astype(np.float)
    spec = np.array(lines[4:])
    spec = spec.astype(np.float)
    wavelength = np.linspace(wl_line[0], wl_line[1], int(wl_line[3]))
    return spec, wavelength

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

def sza_calc(datetime_str, lat, lon):
    jfj_tz = pytz.timezone("Europe/Zurich")
    datetime_obj = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M').astimezone(timezone(timedelta(hours = 1)))
    print(get_azimuth(lat, lon, datetime_obj))

def find_sprange(sim_sp, obs_sp):
    artspec_files = fileList('.')
    art_spec = []
    wv_artsp = []
    for artsp_file in artspec_files:
        wv_artsp_tmp, artspec_tmp= read_spectra(artsp_file)
        art_spec.append(artspec_tmp)
        wv_artsp.append(wv_artsp_tmp)
    art_spec= np.hstack(art_spec)
    wv_artsp = np.hstack(art_spec)
    digi_spec = np.loadtxt('src/data/sroll_17_avril_06_digitized.dat')
    autocorr = fftconvolve(art_spec,digi_spec , mode='same')
    artspec_index = np.where((autocorr == max(autocorr)))[0]
    print(wv_artsp)
    fig, (ax_orgi, ax_corr) = plt.subplots(2,1,sharex = True)
    fig.tight_layout()
    fig.show()


if __name__=="__main__":
    # sza_calc('02/10/1951 11:56', 46.5475, 7.9853)
    find_sprange(None, None)

    # image_slicer.slice( "images/sroll_17_avril.tif", col=6, row=1, save=True, DecompressionBombWarning=False)
    # califiles = glob.glob('data/*calibrated.dat')
    # _cal = np.loadtxt(califiles[1], skiprows = 4)
    # yhat = savgol_filter(_cal, 51, 12)
    # _sim = np.recfromtxt('data/simulated.dat', names = ['wavel', 'spec'])
    # wv_rng = np.linspace(3249,3565,6)
    # wv_min = int(wv_rng[1])
    # wv_max = int(wv_rng[2])
    # wv = np.linspace(wv_min, wv_max, len(_cal))
    # sim_wv=_sim.wavel[( _sim.wavel > wv_min ) & ( _sim.wavel < wv_max )]
    # sim_sp = _sim.spec[(_sim.wavel > wv_min ) &  (_sim.wavel < wv_max )] 
    # # plt.plot(wv, yhat)
    # fig1, ax1 = plt.subplots()
    # # fig2, ax2 = plt.subplots()
    # # ax1.plot(sim_wv, sim_sp)
    # dx = np.mean(np.diff(sim_wv))
    # shift = (np.argmax(signal.correlate(sim_sp, yhat, method='fft')) - len(yhat)) * dx
    # # ax2.plot(wv + shift, _cal, )
    # ax1.plot(wv , yhat)
    # ax1.plot(wv, _cal)
    # plt.show()



