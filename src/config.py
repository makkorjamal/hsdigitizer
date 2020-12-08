import configparser as cp
from os import path
class SpectraConfig:

    def __init__(self):

        self.spConfig = cp.ConfigParser()

    @classmethod
    def fill_config(cls, default, spconf):
        spConf = cls()
        spConf.spConfig['DEFAULT'] = default 
        spConf.spConfig['spectra.conf'] = spconf 
        with open(path.join(spConf.spConfig['spectra.conf']['SpectraPath'], '.sp_config.ini'), 'w') as configfile:
            spConf.spConfig.write(configfile)

    @classmethod
    def read_conf(cls):
        spConf = cls()
        conf = spConf.spConfig
        conf.read('.sp_config.ini')
        return conf

