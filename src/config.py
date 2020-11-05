import configparser as cp

class SpectraConfig:

    def __init__(self):

        self.spConfig = cp.ConfigParser()
        # self.spConfig.read('sp_config.ini')

    @classmethod
    def fill_config(cls, default, spconf):
        spConf = cls()
        spConf.spConfig['DEFAULT'] = default 
        spConf.spConfig['spectra.conf'] = spconf 
        with open('.sp_config.ini', 'w') as configfile:
            spConf.spConfig.write(configfile)

    @classmethod
    def read_conf(cls):
        spConf = cls()
        conf = spConf.spConfig
        conf.read('.sp_config.ini')
        return conf

