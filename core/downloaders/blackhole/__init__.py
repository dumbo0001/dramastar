import os 
import traceback
from core.downloaders.base import BaseDownloader
from tools.common import getDownloadDir

class BlackHole(BaseDownloader):
    name = 'core.downloaders.blackhole'
    use_for = ['directdl', 'torrent']

    config = {
        'label': 'Black hole',
        'description': 'Download the Directdl/Torrent to a specific folder.',
        'options': [
            {
                'name': 'directory',
                'type': 'directory',
                'description': 'Directory where the .txt (or .torrent) file is saved to.',
                'default': getDownloadDir()
            }
        ]
    }
    
    def download(self, filedata, filename):
        print 'Start BlackHole download %r... ' % filename
        directory = self._get_config('directory')
        
        if not directory or not os.path.isdir(directory):
            print 'No directory set for blackhole download'
        else:
            try:
                fullPath = os.path.join(directory, filename)

                try:
                    if not os.path.isfile(fullPath):
                        print 'Downloading %s to %s.', (filename, fullPath)
                        with open(fullPath, 'wb') as f:
                            f.write(filedata)
                        return True
                    else:
                        print 'File %s already exists.', fullPath
                        return True

                except:
                    print 'Failed to download to blackhole %s', traceback.format_exc()
                    pass

            except:
                print 'Failed to download file %s: %s', (filename, traceback.format_exc())
                return False
        
        return False
        