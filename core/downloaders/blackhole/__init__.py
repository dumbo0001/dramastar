import os 
import traceback
from core.downloaders.base import BaseDownloader
from core.config import configmanager

class BlackHole(BaseDownloader):
    name = 'core.downloaders.blackhole'
    
    def __init__(self):
        self.use_for = configmanager.get(self.name, 'use_for').split(',')
    
    def download(self, filedata, filename):
        print 'Start BlackHole download %r... ' % filename
        directory = configmanager.get(self.name, 'directory')
        
        if not directory or not os.path.isdir(directory):
            print 'No directory set for blackhole download'
        else:
            try:
                fullPath = os.path.join(directory, filename)

                try:
                    if not os.path.isfile(fullPath):
                        print 'Downloading %r to %r.', (filename, fullPath)
                        with open(fullPath, 'wb') as f:
                            f.write(filedata)
                        return True
                    else:
                        print 'File %s already exists.', fullPath
                        return True

                except:
                    print 'Failed to download to blackhole %r', \
                        traceback.format_exc()
                    pass

            except:
                print 'Failed to download file %r: %r', (filename, \
                    traceback.format_exc())
                return False
        
        return False
        