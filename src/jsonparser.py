import json
import os
from spectrum import Spectrum
class JsonParser:
    """Class to save spectra in a json file"""

    def __init__(self,jpath, spectrums = []):
        self.spectrums = spectrums
        self.jpath = jpath

    def save_json(self):
        #save the spectrum.py object in a json file

       with open(os.path.join("spectra_file.json"), "w") as write_file:
           json.dump([obj.__dict__ for obj in self.spectrums], write_file)

    # def update_json(self, filename, dt = []):

    #     with open(os.path.join(self.jpath,filename), "r") as read_file:
    #         data = json.load(read_file)
    #         [data.append([d.update(dd) for dd in dt]) for d in data]

    #    with open(os.path.join(self.jpath,"spectra_file.json"), "w") as write_file:
    #        json.dump(data, write_file)

    def read_json(self,filename):
        #read the saved json.
        #saved in a Spectrum object.

        with open(os.path.join(filename), "r") as read_file:
            data = json.load(read_file)
        for d in data:
            sp = Spectrum(d['img_name'],d['sp_name'],d['calsp_name'], d['calsplines_name'], d['sp_range'])
            self.spectrums.append(sp)
        return self.spectrums 
