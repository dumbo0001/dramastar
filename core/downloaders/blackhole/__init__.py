import os 
import traceback
from core.downloaders.base import BaseDownloader
from core.config import configmanager
from core.entities.models import ERROR, EPISODE_STATUS_DOWNLOADED

class BlackHole(BaseDownloader):    
    def __init__(self):
        self.name = 'core.downloaders.blackhole'
        self.enabled = configmanager.getboolean(self.name, 'enabled')
        self.use_for = configmanager.get(self.name, 'use_for').split(',')
    
    def download(self, filedata, filename, additional_arguments):
        print 'Start BlackHole download %r... ' % filename
        return_status = ERROR
        directory = configmanager.get(self.name, 'directory')
        
        if not directory or not os.path.isdir(directory):
            print 'No directory set for blackhole download'
            return_status = ERROR
        else:
            try:
                fullPath = os.path.join(directory, filename)
                
                print 'Downloading %r to %r.', (filename, fullPath)
                with open(fullPath, 'wb') as f:
                    f.write(filedata)
                return_status = EPISODE_STATUS_DOWNLOADED

            except:
                print 'Failed to download file %r: %r', (filename, \
                    traceback.format_exc())
                return_status = ERROR
        
        return return_status
        