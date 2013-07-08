import re
import urllib2
from core.downloaders.base import BaseDownloader

class JDownloader(BaseDownloader):
    name = 'core.downloaders.jdownloader'
    use_for = ['directdl']
    
    last_domains = []
    
    def download(self, filedata, filename):
        print 'Start Jdownloader download %r... ' % filename
        links = re.findall('(?P<url>https?://[^\s]+)', filedata)
        # Send to JDownloader
        grabbed = False
        
        links = [d for d in links if 'depositfiles' not in d]
        
        for link in links:
            if 'depositfiles' in link:
                continue
                
            regex = re.compile('https?://(?P<domain>[^\s]+?)/')
            domain = regex.match(link).group('domain')
            
            if not grabbed and domain not in self.last_domains:
                response = urllib2.urlopen( \
                    'http://localhost:10025/action/add/links/grabber0/' + \
                    'start1/' + link)
                self.last_domains.append(domain)
                grabbed = True
                
        if not grabbed:
            
            response = urllib2.urlopen( \
                'http://localhost:10025/action/add/links/grabber0/' + \
                'start1/' + links[0])
            
            regex = re.compile('https?://(?P<domain>[^\s]+?)/')
            domain = regex.match(link).group('domain')
            
            self.last_domains = []
            self.last_domains.append(domain)
        
        return True