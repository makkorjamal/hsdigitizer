import image_slicer
import sys
import csv
from sklearn.preprocessing import normalize
import pytz
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import glob
import image_slicer 
from sklearn.impute import SimpleImputer
from scipy.signal import savgol_filter, fftconvolve, correlate, coherence, lfilter
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

def update_cal_spec(savepath,name, new_wl):
    
    sppath = os.path.join(savepath, name)
    with open(sppath) as f:
        lines = f.readlines()

    wl_line = np.fromstring(lines[3], dtype = np.float16, sep = '\t')
    lines[3][0].replace(lines[3][0], str(new_wl[0]) )
    lines[3][1].replace(lines[3][1], str(new_wl[1]) )
    new_sp_file = os.path.join(savepath, name)
    with open(new_sp_file, 'w+') as cal_fil_id:
        cal_fil_id.write(''.join(lines) + '\n')
        # writer = csv.writer(cal_fil_id, delimiter=' ',  quoting=csv.QUOTE_NONE)
        # writer.writerow(lines)
        print("wrote new file")


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
    artspec_files = sorted(fileList('./artspec/'))
    art_spec = []
    wv_artsp = []
    # for artsp_file in artspec_files:
    #     wv_artsp_tmp, artspec_tmp= read_spectra(artsp_file)
    #     art_spec.append(artspec_tmp)
    #     wv_artsp.append(wv_artsp_tmp)

    # art_spec= np.hstack(art_spec)
    # wv_artsp = np.hstack(wv_artsp)
    _sim = np.recfromtxt('simulated.dat', names = ['wavel', 'spec'])
    art_spec =np.hstack(_sim['spec'])
    wv_artsp= np.hstack(_sim['wavel'])
    digi_spec = np.hstack(normalize(np.loadtxt('data/sroll_17_avril_02_digitized.dat').reshape(1,-1)))
    # digi_spec = np.flip(digi_spec)
    autocorr = correlate(art_spec,digi_spec , mode='same', method = 'fft')
    artspec_index = np.where((autocorr == max(autocorr)))[0] 
    print(wv_artsp[artspec_index])
    fig, ax = plt.subplots()
    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()
    ax.plot(wv_artsp, art_spec)
    ax1.plot(np.arange(len(autocorr)), autocorr)
    ax2.plot(np.arange(len(digi_spec)), digi_spec)
    plt.show()


if __name__=="__main__":
    # sza_calc('02/10/1951 11:56', 46.5475, 7.9853)
    # find_sprange(None, None)

    image_slicer.slice(sys.argv[1], col=int(sys.argv[2]), row=1, save=True, DecompressionBombWarning=False)
