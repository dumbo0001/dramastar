import logging
import os 
import traceback
from core.downloaders.base import BaseDownloader
from core.config import configmanager
from core.entities.models import ERROR, EPISODE_STATUS_DOWNLOADED

log = logging.getLogger(__name__)

class BlackHole(BaseDownloader):    
    def __init__(self):
        self.name = 'core.downloaders.blackhole'
        self.enabled = configmanager.getboolean(self.name, 'enabled')
        self.use_for = configmanager.get(self.name, 'use_for').split(',')
    
    def download(self, filedata, filename, additional_arguments):
        log.info('Start downloading of %s with %s...' % (filename, \
            self.name))
        return_status = ERROR
        directory = configmanager.get(self.name, 'directory')
        
        if not directory or not os.path.isdir(directory):
            log.warning('No directory configured...')
            return_status = ERROR
        else:
            try:
                fullPath = os.path.join(directory, filename)
                
                log.info('Downloading to %r.' % fullPath)
                with open(fullPath, 'wb') as f:
                    f.write(filedata)
                return_status = EPISODE_STATUS_DOWNLOADED

            except:
                log.warning('Downloading of %s failed: %r', (filename, \
                    traceback.format_exc()))
                return_status = ERROR
        
        log.info('Finished downloading...')
        return return_status
        