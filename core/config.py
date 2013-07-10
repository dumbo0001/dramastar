import ConfigParser
from tools.common import get_absolute_path

class ConfigManager(object):
    _configmanager = None
    
    def __init__(self):
        self._configmanager = ConfigParser.SafeConfigParser()
        self._configmanager.read(get_absolute_path('core.ini'))
        
    def get(self, section, option):
        return self._configmanager.get(section, option)
        
    def getboolean(self, section, option):
        return self._configmanager.getboolean(section, option)
        
    def getint(self, section, option):
        return self._configmanager.getint(section, option)
        
    def getlist(self, section, option):
        return self._configmanager.get(section, option).split(',')


configmanager = ConfigManager()